// Source: https://git.lumorian.org/Lumorian/pi-auto-continue aaaf49f (MIT). Local changes: last-sentence check, thinking-only stop, English nudge and notices (Max Architect, 2026-11-17), unchanged-context guard (P1.9, 2026-11-18).
/**
 * auto-continue: 当模型"说到一半"就结束回合时自动续跑。
 *
 * 症状:模型(尤其 flash 档)输出一段"接下来我要测 X:"之类的分析文本后,
 * 不发起工具调用就 end_turn,导致回合中断,用户被迫手动输入"继续"。
 *
 * 机制:在 agent_before_settle(最终结算边界)检查最后一条 assistant 消息——
 * 若为纯文本(无 toolCall)、stopReason=stop、且文本符合"宣布了下一步却没做"的
 * 特征,则追加一条提示条目并返回 { continue: true } 强制再跑一次模型请求。
 *
 * 防失控:每个 agent run 最多自动续 MAX_AUTO_CONTINUES 次;若上下文未推进
 * (工具调用次数未增加或回复文本与上次续跑完全一致)则不再续跑;用户主动问
 * 问题时(以 ?/？ 结尾)不触发;/autocontinue 命令可随时开关。
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const MAX_AUTO_CONTINUES = 5;

/** 中文"宣布下一步"开头(可带编号/列表前缀) */
const ZH_ANNOUNCE =
	/^(?:\d+[.、)]\s*|[-*]\s*)?(?:接下来|下一步|现在|首先|然后|再|先|开始|接着|继续|测试|测一下|验证|确认|运行|执行|检查|查看|读取|写入|修改|创建|删除|尝试|重新|再次)/;
/** 英文"宣布下一步"开头 */
const EN_ANNOUNCE =
	/^\s*(?:Let me|Now (?:let's|let me|I)|I'll|I will|I am going to|Next,?|First,?|Then,?|OK,? (?:so )?(?:let|now)|Alright,? (?:so )?(?:let|now)|Running|Testing|Checking|Trying|Proceeding|Continuing)/i;
/** 英文"口头承诺/待命不执行"短语 (Max Architect, 2026-11-18) */
const EN_DEFER =
	/\b(?:standing by(?: to)?|will run|will execute|ready to (?:run|execute|proceed|queue)|whenever you confirm|(?:I'll|I will|Let me)\s+(?:pick|run|execute|write|check|queue|create|call|proceed))\b/i;

function lastLine(text: string): string {
	const lines = text.trimEnd().split("\n").filter((l) => l.trim() !== "");
	const line = (lines[lines.length - 1] ?? "").trim();
	// Max Architect 2026-11-17 (Derrick t2343s8395): check the last sentence, not the whole last line.
	const sentences = line.split(/(?<=[.!。！])\s+/).filter((x) => x.trim() !== "");
	return (sentences[sentences.length - 1] ?? line).trim();
}

/** 判断文本是否是"话说一半/宣布了动作却收工" */
function isPrematureStop(text: string): boolean {
	const t = text.trimEnd();
	if (!t) return false;
	// 用户提问式结尾 → 合法收工
	if (/[?？]\s*$/.test(t)) return false;
	// 以冒号结尾:典型的"宣布:然后没了"
	if (/[:：]\s*$/.test(t)) return true;
	// 省略号结尾:话说一半
	if (/(?:\.\.\.|…)\s*$/.test(t)) return true;
	// 未闭合的代码块(``` 数量为奇数):输出中途断了
	if ((t.match(/```/g) ?? []).length % 2 === 1) return true;
	// 最后一行是"宣布语气"
	const line = lastLine(t);
	if (ZH_ANNOUNCE.test(line) && line.length <= 120) return true;
	if ((EN_ANNOUNCE.test(line) || EN_DEFER.test(line)) && line.length <= 400) return true;
	return false;
}

function countToolCalls(msgs: ReadonlyArray<{ role?: string; content?: unknown }>): number {
	let total = 0;
	for (const m of msgs) {
		if (m.role !== "assistant" || !Array.isArray(m.content)) continue;
		for (const b of m.content) {
			if (b && typeof b === "object" && (b as { type?: unknown }).type === "toolCall") {
				total++;
			}
		}
	}
	return total;
}

export default function (pi: ExtensionAPI) {
	let enabled = true;
	let continuationsThisRun = 0;
	let lastNudgedToolCalls: number | null = null;
	let lastNudgedText: string | null = null;

	const resetState = () => {
		continuationsThisRun = 0;
		lastNudgedToolCalls = null;
		lastNudgedText = null;
	};

	pi.on("session_start", resetState);
	pi.on("agent_start", resetState);

	pi.registerCommand("autocontinue", {
		description: "Toggle auto-continue when the model stops after announcing a step",
		handler: async (_args, ctx) => {
			enabled = !enabled;
			if (ctx.hasUI) {
				ctx.ui.notify(`auto-continue ${enabled ? "on" : "off"}`, "info");
			}
		},
	});

	pi.on("agent_before_settle", (event, ctx) => {
		if (!enabled) return;
		if (event.continue) return; // 已有其他 handler 请求续跑
		if (event.outcome !== "completed") return; // aborted / error 不掺和
		if (continuationsThisRun >= MAX_AUTO_CONTINUES) {
			if (ctx.hasUI) {
				ctx.ui.notify(
					`auto-continue: already continued ${MAX_AUTO_CONTINUES} times this run; stopping, needs a person`,
					"warning",
				);
			}
			return;
		}

		// 找最后一条 assistant 消息
		const msgs = event.context.contextMessages;
		let last: (typeof msgs)[number] | undefined;
		for (let i = msgs.length - 1; i >= 0; i--) {
			if (msgs[i].role === "assistant") {
				last = msgs[i];
				break;
			}
		}
		if (!last || last.role !== "assistant") return;

		// 只处理"模型自己收工"(stop),且没有任何工具调用
		if (last.stopReason !== "stop") return;
		if (last.content.some((b) => b.type === "toolCall")) return;

		const text = last.content
			.filter((b): b is { type: "text"; text: string } => b.type === "text")
			.map((b) => b.text)
			.join("\n");
		// Max Architect 2026-11-17 (Derrick t2346s8413): also continue a thinking-only stop
		// (thinking but no text and no tool call), like pi-hodor's autoContinueOnThinkingOnlyStop.
		const thinkingOnly =
			!text.trim() &&
			last.content.some((b: any) => b.type === "thinking" && typeof b.thinking === "string" && b.thinking.trim() !== "");
		if (!thinkingOnly) {
			if (!text.trim()) return;
			if (!isPrematureStop(text)) return;
		}

		// P1.9 guard: never re-prompt an unchanged context (same tool-call count or identical reply text).
		const totalToolCalls = countToolCalls(msgs);
		const trimmedText = text.trim();
		if (
			lastNudgedToolCalls !== null &&
			(totalToolCalls === lastNudgedToolCalls || trimmedText === lastNudgedText)
		) {
			if (ctx.hasUI) {
				ctx.ui.notify("auto-continue: context unchanged since last nudge; stopping", "warning");
			}
			return;
		}

		continuationsThisRun++;
		lastNudgedToolCalls = totalToolCalls;
		lastNudgedText = trimmedText;
		if (ctx.hasUI) {
			ctx.ui.notify(
				`auto-continue: model stopped after announcing a step; continuing (${continuationsThisRun}/${MAX_AUTO_CONTINUES})`,
				"warning",
			);
		}
		return {
			entries: [
				{
					type: "custom_message",
					customType: "auto-continue-nudge",
					content:
						"[auto-continue] Your last message announced a next step but ended the turn without making a tool call. Continue now: make the tool call you just described directly. Do not repeat the analysis, write a long plan, or ask the user a question.",
					display: false,
				},
			],
			continue: true,
		};
	});
}
