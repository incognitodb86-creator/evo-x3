/**
 * loop-guard: stops the run on two kinds of loops.
 *  Rule 1 (2026-10-30, Forge/Sydney): the SAME tool call (same tool name + identical
 *    args) 3 times in a row.
 *  Rule 2 (Max Architect 3, 2026-11-13, Derrick t1355): the parody writer check
 *    (submit_parody_run.py, e.g. `writer-run`) called more than RUN_LIMIT times on the
 *    same run folder in one agent run, even when the arguments differ each time
 *    (Gemma 2026-11-13 retried 40-70 slightly varied writer-run calls).
 * No network, no file I/O, no env/credential access. Pure in-memory counters.
 * Rule 1 modelled on the tool_call hook in alisorcorp/pi-small-model-addons@e251d0b
 * repetition-loop-abort.ts.
 *
 * 2026-11-15 U31 (Antigravity SF-01, Derrick t1819u): parse CLI flags without
 * assuming positional order, keep Linux path case, and do not clear per-folder
 * runCounts on agent_settled or on a trip (only session_start resets them).
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const LIMIT = 3;
const RUN_LIMIT = 4; // 5th check call on the same run folder is blocked

function stable(v: unknown): string {
  if (v === null || typeof v !== "object") return JSON.stringify(v);
  if (Array.isArray(v)) return "[" + v.map(stable).join(",") + "]";
  const o = v as Record<string, unknown>;
  return "{" + Object.keys(o).sort().map((k) => JSON.stringify(k) + ":" + stable(o[k])).join(",") + "}";
}

/** Split a shell-like command into tokens, honoring single/double quotes. */
export function tokenizeCmd(cmd: string): string[] {
  const out: string[] = [];
  let cur = "";
  let quote: "'" | '"' | null = null;
  for (let i = 0; i < cmd.length; i++) {
    const c = cmd[i];
    if (quote) {
      if (c === quote) quote = null;
      else cur += c;
      continue;
    }
    if (c === "'" || c === '"') {
      quote = c;
      continue;
    }
    if (/\s/.test(c)) {
      if (cur) { out.push(cur); cur = ""; }
      continue;
    }
    cur += c;
  }
  if (cur) out.push(cur);
  return out;
}

function isFlag(t: string): boolean {
  return t.startsWith("-");
}

const BOOL_FLAGS = /^(--continued|--s3-in-frame|--queue|--dry-run|--help|-h|--no-[a-z0-9_-]+|--yes-[a-z0-9_-]+)$/i;

/** First run-dir token: --run-dir/--rundir value, or first non-flag after the script / writer-run. */
export function runDirFromCmd(cmd: string): string {
  const tokens = tokenizeCmd(cmd);
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    const eq = t.match(/^--run-dir=(.+)$/i) || t.match(/^--rundir=(.+)$/i);
    if (eq) return eq[1];
    if (/^--run-dir$/i.test(t) || /^--rundir$/i.test(t)) return tokens[i + 1] ?? "";
  }
  const idx = tokens.findIndex((t) => /(?:submit_parody_run|render_writer_pipeline)(?:\.py)?/i.test(t));
  const start = idx >= 0 ? idx + 1 : 0;
  for (let i = start; i < tokens.length; i++) {
    const t = tokens[i];
    if (isFlag(t)) {
      if (!t.includes("=") && !BOOL_FLAGS.test(t) && tokens[i + 1] && !isFlag(tokens[i + 1])) i++;
      continue;
    }
    if (/^writer-run$/i.test(t)) continue;
    return t;
  }
  return "";
}

export function normalizeRunDir(dir: string): string {
  let norm = dir.replace(/\\/g, "/").replace(/\/+$/, "");
  // Windows paths are case-insensitive; Linux paths are not.
  if (typeof process !== "undefined" && process.platform === "win32") norm = norm.toLowerCase();
  return norm;
}

/** Returns a per-run-folder key when the call runs submit_parody_run.py or render_writer_pipeline.py, else null. */
export function parodyRunKey(input: unknown): string | null {
  if (input === null || typeof input !== "object") return null;
  const cmd = (input as Record<string, unknown>).command;
  if (typeof cmd !== "string" || !/(?:submit_parody_run|render_writer_pipeline)/i.test(cmd)) return null;
  const norm = normalizeRunDir(runDirFromCmd(cmd));
  return "parody::" + (norm || "?");
}

export default function (pi: ExtensionAPI) {
  let last = "";
  let count = 0;
  const runCounts = new Map<string, number>();
  const resetStreak = () => { last = ""; count = 0; };
  const resetAll = () => { resetStreak(); runCounts.clear(); };
  pi.on("session_start", resetAll);
  // agent_settled fires between tool rounds; clearing runCounts there let the writer retry cap reset (SF-01).
  pi.on("agent_settled", resetStreak);

  pi.on("tool_call", async (event, ctx) => {
    // Rule 2: repeated writer checks on one run folder, args may differ.
    let runKey: string | null = null;
    try { runKey = parodyRunKey(event.input); } catch { runKey = null; }
    if (runKey) {
      const n = (runCounts.get(runKey) ?? 0) + 1;
      runCounts.set(runKey, n);
      if (n > RUN_LIMIT) {
        resetStreak();
        if (ctx.hasUI) ctx.ui.notify(`loop-guard: submit_parody_run called ${n}x on the same run folder - stopping`, "warning");
        return {
          block: true,
          terminate: true,
          reason: `loop-guard: submit_parody_run has already run ${RUN_LIMIT} times on this run folder in this run. Stopping; report the last NOT_READY reasons to Derrick instead of retrying.`,
        };
      }
    }

    // Rule 1: identical call repeated.
    let key: string;
    try { key = event.toolName + "::" + stable(event.input); } catch { key = event.toolName + "::?"; }
    if (key === last) count++; else { last = key; count = 1; }
    if (count < LIMIT) return undefined;
    resetStreak();
    if (ctx.hasUI) ctx.ui.notify(`loop-guard: "${event.toolName}" called ${LIMIT}x in a row with identical args - stopping`, "warning");
    return {
      block: true,
      terminate: true,
      reason: `loop-guard: this is the ${LIMIT}rd identical "${event.toolName}" call in a row with the same arguments. Stopping the run; change approach instead of repeating it.`,
    };
  });
}
