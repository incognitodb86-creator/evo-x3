/**
 * protected-paths - Pi extension (forgesafe 2026-10-20, Derek-approved). Adapted from Pi's examples/extensions/protected-paths.ts.
 *
 * Hard-denies (UI and headless runs alike; not affected by pi-permission-system yolo) any write/edit, and any bash/powershell
 * command that looks like it writes (Set-Content, Out-File, cp, mv, rm, tee, sed -i, >, >>, [IO.File]::Write*, git checkout/restore ...),
 * when a target resolves into one of these:
 *   - any ComfyUI\user\** folder (live workflows, settings) and any *.app.json under a ComfyUI folder
 *   - C:\AI\director\config\llama-swap.yaml (llama-swap runs with -watch-config: a save reloads it live)
 *   - C:\AI\strata*\*.json (Strata run configs)
 *   - ~/.pi/agent/** (Pi settings, models, permission policy, sessions)
 *   - ralph.ps1 / chain.ps1 anywhere, and 5slock\ralph*\PROMPT.md (the loop harness)
 *   - C:\Apps\** except finance-app-rebuild (and its .git/.pi)
 *   - C:\AI\director\.pi\** (the guard extensions themselves)
 *   - p7lock 2026-10-20: GPU pipeline scripts in C:\AI\community\scripts (batch_queue, comm, prompt_writer, p3-p6*, sy_1min*, mk_*, *.ps1),
 *     gpu_guard/gpu_lock/overnight_chain.ps1, and the P7 harness files (p7\KNOBS.md, p7\jobs, p7\reviews, runs\P6_RANKING.*, p7_budget.json)
 * Reading these paths stays allowed. Shell detection is best-effort (static text check), not a sandbox: a script file that writes
 * a protected path internally is not seen here. Pure helpers are exported for tests/pi/protected-paths.test.mjs.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";
import { join } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { appendFileSync, mkdirSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { win32 } from "node:path";

export interface PathViolation {
	id: string;
	path: string;
	reason: string;
}

const HOME = (process.env.USERPROFILE || homedir()).replace(/\\/g, "/").replace(/\/+$/, "").toLowerCase();

/** Normalizes a Windows / Git Bash / ~ path to lowercase forward-slash absolute form. */
export function normalizePath(raw: string, cwd: string): string {
	let p = raw.trim().replace(/^["']|["']$/g, "");
	if (!p) return "";
	p = p.replace(/\\/g, "/");
	if (p === "~" || p.startsWith("~/")) p = HOME + p.slice(1);
	else if (/^\$(?:env:)?(?:USERPROFILE|HOME)(?=\/|$)/i.test(p)) p = p.replace(/^\$(?:env:)?(?:USERPROFILE|HOME)/i, HOME);
	const gitBash = /^\/([a-zA-Z])(\/.*)?$/.exec(p);
	if (gitBash) p = `${gitBash[1]}:${gitBash[2] ?? "/"}`;
	const abs = win32.resolve(cwd.replace(/\//g, "\\"), p.replace(/\//g, "\\"));
	return abs.replace(/\\/g, "/").toLowerCase();
}

interface Rule {
	id: string;
	test: (p: string) => boolean;
	reason: string;
}

const RULES: Rule[] = [
	{ id: "comfyui-user", test: (p) => /\/comfyui\/user(?:\/|$)/.test(p), reason: "ComfyUI\\user (live workflows and settings) is read-only for Forge." },
	{ id: "comfyui-live-workflow", test: (p) => /\/comfyui\/.*\.app\.json$/.test(p), reason: "live ComfyUI *.app.json workflows are read-only for Forge." },
	{ id: "llama-swap-config", test: (p) => p === "c:/ai/director/config/llama-swap.yaml", reason: "llama-swap.yaml hot-reloads (-watch-config); only the supervisor edits it, and only when the GPU is idle." },
	{ id: "strata-config", test: (p) => /^c:\/ai\/strata[^/]*\/[^/]+\.json$/.test(p), reason: "Strata run configs are supervisor-only." },
	{ id: "pi-agent-config", test: (p) => p === `${HOME}/.pi/agent` || p.startsWith(`${HOME}/.pi/agent/`), reason: "~/.pi/agent (Pi settings, models, permission policy) is supervisor-only." },
	{
		id: "loop-harness",
		test: (p) => /\/(?:ralph|chain)\.ps1$/.test(p) || /\/5slock\/ralph[^/]*\/prompt\.md$/.test(p),
		reason: "the loop harness (ralph.ps1, chain.ps1, PROMPT.md) is supervisor-only.",
	},
	{ id: "apps", test: (p) => (p === "c:/apps" || p.startsWith("c:/apps/")) && !((p === "c:/apps/finance-app-rebuild" || p.startsWith("c:/apps/finance-app-rebuild/")) && !p.startsWith("c:/apps/finance-app-rebuild/.git") && !p.startsWith("c:/apps/finance-app-rebuild/.pi")), reason: "C:\\Apps is off-limits except C:\\Apps\\finance-app-rebuild (Derek 2026-10-20: Forge finishes ALI-55); live finance-app stays protected." },
	{ id: "guard-extensions", test: (p) => p === "c:/ai/director/.pi" || p.startsWith("c:/ai/director/.pi/"), reason: "the Forge guard extensions are supervisor-only." },
	// p7lock 2026-10-20 (Derek: "do whatever you recommend"): the GPU pipeline and the P7 harness files (pi-permissions.jsonc denies the
	// write/edit tools too; this also covers shell writes from the powershell tool).
	{
		id: "gpu-pipeline",
		test: (p) =>
			/^c:\/ai\/community\/scripts\/(?:batch_queue|comm|prompt_writer|p6_review|p[3-6][^/]*|sy_1min[^/]*|mk_[^/]*)\.py$/.test(p) ||
			/^c:\/ai\/community\/scripts\/[^/]+\.ps1$/.test(p) ||
			/^c:\/ai\/director\/scripts\/(?:gpu_guard|gpu_lock|overnight_chain)\.ps1$/.test(p),
		reason: "the render/review pipeline scripts and the GPU guard/lock/overnight chain are supervisor-only. Request GPU work through p7\\JOB_REQUEST.json.",
	},
	{
		id: "p7-harness",
		test: (p) =>
			p === "c:/ai/community/p7/knobs.md" ||
			/^c:\/ai\/community\/p7\/(?:jobs|reviews)(?:\/|$)/.test(p) ||
			/^c:\/ai\/community\/runs\/p6_ranking\./.test(p) ||
			p === `${HOME}/5slock/ralph-community/logs/p7_budget.json`,
		reason: "KNOBS.md, p7\\jobs, p7\\reviews, runs\\P6_RANKING.* and the GPU budget are written by the harness only (it restores them and stops the loop).",
	},
];

export function checkPath(raw: string, cwd: string): PathViolation | null {
	const p = normalizePath(raw, cwd);
	if (!p) return null;
	for (const r of RULES) if (r.test(p)) return { id: r.id, path: p, reason: r.reason };
	return null;
}

const HARMLESS_REDIRECTS = /\d?>\s*\$null|\d?>&\d|\d?>\s*\/dev\/null|\d?>\s*nul\b|\|\s*Out-Null/gi;
const WRITE_HINT =
	/(?<![\w-])(?:Set-Content|Add-Content|Out-File|Clear-Content|New-Item|Copy-Item|Move-Item|Remove-Item|Rename-Item|Export-\w+|sc|ac|ni|ri|mi|cpi|cp|mv|rm|del|erase|ren|rename|move|copy|xcopy|robocopy|tee|touch|truncate|install|ln|mklink|attrib|git\s+(?:checkout|restore|apply|mv|rm|stash))(?![\w-])|(?<![=-])>|\bsed\s+-[a-z]*i|WriteAll(?:Text|Bytes|Lines)|AppendAll(?:Text|Lines)|\.write(?:_text|_bytes)?\(|\bopen\([^)]*,\s*['"][wax+]/i;
const EMBEDDED_PATH = /(?:[a-zA-Z]:[\\/]|~[\\/]|(?<![\w.])\/[a-zA-Z]\/|\$env:USERPROFILE[\\/])[^\s"'`;|&<>(),]*/g;
const TOKEN = /"([^"]*)"|'([^']*)'|([^\s"'|;&<>()=,]+)/g;

/** bash/powershell: blocks when the command looks like a write AND any argument resolves to a protected path. */
export function checkShell(command: string, cwd: string): PathViolation | null {
	const cleaned = command.replace(HARMLESS_REDIRECTS, " ");
	if (!WRITE_HINT.test(cleaned)) return null;
	for (const m of cleaned.matchAll(TOKEN)) {
		const tok = (m[1] ?? m[2] ?? m[3] ?? "").replace(/^-\w+:/, "");
		if (!tok || /^-/.test(tok) || /^[a-z][\w+.-]*:\/\//i.test(tok)) continue;
		const v = checkPath(tok, cwd);
		if (v) return v;
	}
	// paths embedded inside quoted code, e.g. python -c "open('C:/x','w')" or [IO.File]::WriteAllText("C:\x", ...)
	for (const m of cleaned.matchAll(EMBEDDED_PATH)) {
		const v = checkPath(m[0], cwd);
		if (v) return v;
	}
	return null;
}

function asRecord(v: unknown): Record<string, unknown> {
	return typeof v === "object" && v !== null ? (v as Record<string, unknown>) : {};
}

export function evaluate(toolName: string, input: unknown, cwd: string): PathViolation | null {
	const args = asRecord(input);
	if (toolName === "write" || toolName === "edit") return typeof args.path === "string" ? checkPath(args.path, cwd) : null;
	if (toolName === "bash" || toolName === "powershell") return typeof args.command === "string" ? checkShell(args.command, cwd) : null;
	return null;
}

export function blockMessage(v: PathViolation): string {
	return `Blocked by protected-paths [${v.id}]: ${v.path} - ${v.reason} Do not retry or work around this; note it in your final report (or write STOP_RALPH if the task needs it).`;
}

function logEvent(event: Record<string, unknown>): void {
	try {
		const dir = `${tmpdir()}\\pi-tool-outputs`;
		mkdirSync(dir, { recursive: true });
		appendFileSync(`${dir}\\guard-events.jsonl`, `${JSON.stringify({ ts: new Date().toISOString(), ext: "protected-paths", ...event })}\n`, "utf8");
	} catch {
		// logging must never affect tool execution
	}
}

// forgeopen 2026-10-23 (ALI-163, Derrick 1:53 PM CT "Really anything secrets cause it's gotta do the finance stuff"): headless Forge sessions
// skip these path rules; headless-guard-and-truncate blocks secrets for them. Same switch as the guard ("forgeOpen" in headless-guard-allowlist.json).
export function forgeOpenCwd(cwd: string): boolean {
	if (process.env.PI_GUARD_FORGE_OPEN === "0") return false;
	try {
		const f = join(dirname(fileURLToPath(import.meta.url)), "headless-guard-allowlist.json");
		const al = JSON.parse(readFileSync(f, "utf8"));
		if (al.forgeOpen === false) return false;
		const roots: string[] = al.denylistCwdRoots ?? ["C:/Users/derek/5slock", "C:/AI/community"];
		const c = cwd.replace(/\\/g, "/").replace(/\/+$/, "").toLowerCase();
		return roots.some((r) => { const x = r.replace(/\\/g, "/").replace(/\/+$/, "").toLowerCase(); return c === x || c.startsWith(x + "/"); });
	} catch { return false; }
}

export default function protectedPaths(pi: ExtensionAPI): void {
	pi.on("tool_call", async (event, ctx) => {
		try {
			if (ctx.hasUI === false && forgeOpenCwd(ctx.cwd || process.cwd())) return undefined; // forgeopen: the headless guard owns Forge (secrets only)
			const v = evaluate(event.toolName, event.input, ctx.cwd || process.cwd());
			if (!v) return undefined;
			logEvent({ kind: "block", tool: event.toolName, rule: v.id, path: v.path });
			if (ctx.hasUI) ctx.ui.notify(`Blocked write to protected path: ${v.path}`, "warning");
			return { block: true, reason: blockMessage(v) };
		} catch (error) {
			logEvent({ kind: "guard-error", tool: event.toolName, error: String(error) });
			return { block: true, reason: "Blocked by protected-paths: internal error while checking this call." };
		}
	});
}
