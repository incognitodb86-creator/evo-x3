/**
 * loop-guard: stops the run on two kinds of loops.
 *  Rule 1 (2026-10-30, Forge/Sydney): the SAME tool call (same tool name + identical
 *    args) 3 times in a row.
 *  Rule 2 (Max Architect 3, 2026-11-13, Derrick t1355; scoped 2026-11-18, Derrick t2380u):
 *    the parody QUEUE call (submit_parody_run.py ... --queue) issued more than RUN_LIMIT times
 *    on the same run folder in one agent run, even when the arguments differ each time
 *    (Gemma 2026-11-13 retried 40-70 slightly varied writer-run calls).
 *    Dry runs are NOT counted: render_writer_pipeline.py calls submit_parody_run.py writer-run
 *    internally as a dry run and self-retries the build once, so counting it made one intended
 *    pipeline run burn 2+ units of the queue budget and blocked the first real --queue call.
 * No network, no file I/O, no env/credential access. Pure in-memory counters.
 * Rule 1 modelled on the tool_call hook in alisorcorp/pi-small-model-addons@e251d0b
 * repetition-loop-abort.ts.
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

/**
 * Returns a per-run-folder key ONLY for a real queue request (submit_parody_run.py ... --queue).
 * Dry runs (writer-run without --queue, and render_writer_pipeline.py, which dry-runs internally)
 * are not counted - the pipeline's own build retries are not a queue loop.
 */
export function parodyRunKey(input: unknown): string | null {
  if (input === null || typeof input !== "object") return null;
  const cmd = (input as Record<string, unknown>).command;
  // Only real runs (python ... script.py), not greps/reads that mention the name (Max Architect, 2026-11-18).
  if (typeof cmd !== "string" || !/\bpy(?:thon)?(?:3(?:\.\d+)?)?(?:\.exe)?["']?\s+(?:-\S+\s+)*[^|;&\n]*?submit_parody_run\.py/i.test(cmd)) return null;
  if (!/(?:^|\s)--queue(?:\s|$)/.test(cmd)) return null; // dry run: not a queue attempt
  const m = cmd.match(/submit_parody_run(?:\.py)?["']?\s+([a-z][\w-]*)\s+(?:--run-dir\s+)?(?:"([^"]+)"|'([^']+)'|(\S+))/i);
  const dir = m ? (m[m.length - 3] ?? m[m.length - 2] ?? m[m.length - 1] ?? "") : "";
  const norm = dir.replace(/\\/g, "/").replace(/\\+$/, "").toLowerCase();
  return "parody::" + (norm || "?");
}

export default function (pi: ExtensionAPI) {
  let last = "";
  let count = 0;
  const runCounts = new Map<string, number>();
  const reset = () => { last = ""; count = 0; runCounts.clear(); };
  pi.on("session_start", reset);
  pi.on("agent_settled", reset);

  pi.on("tool_call", async (event, ctx) => {
    // Rule 2: repeated writer checks on one run folder, args may differ.
    let runKey: string | null = null;
    try { runKey = parodyRunKey(event.input); } catch { runKey = null; }
    if (runKey) {
      const n = (runCounts.get(runKey) ?? 0) + 1;
      runCounts.set(runKey, n);
      if (n > RUN_LIMIT) {
        reset();
        if (ctx.hasUI) ctx.ui.notify(`loop-guard: --queue requested ${n}x on the same run folder - stopping`, "warning");
        return {
          block: true,
          terminate: true,
          reason: `loop-guard: --queue has already been requested ${RUN_LIMIT} times on this run folder in this run. Stopping; report the last result to Derrick instead of re-queueing.`,
        };
      }
    }

    // Rule 1: identical call repeated.
    let key: string;
    try { key = event.toolName + "::" + stable(event.input); } catch { key = event.toolName + "::?"; }
    if (key === last) count++; else { last = key; count = 1; }
    if (count < LIMIT) return undefined;
    reset();
    if (ctx.hasUI) ctx.ui.notify(`loop-guard: "${event.toolName}" called ${LIMIT}x in a row with identical args - stopping`, "warning");
    return {
      block: true,
      terminate: true,
      reason: `loop-guard: this is the ${LIMIT}rd identical "${event.toolName}" call in a row with the same arguments. Stopping the run; change approach instead of repeating it.`,
    };
  });
}