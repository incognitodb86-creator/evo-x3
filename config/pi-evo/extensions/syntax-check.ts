/**
 * syntax-check (L7, unified plan e0c446f): after write/edit tool calls, run a fast local syntax check
 * (python3 -m py_compile, bash -n, or jq empty) and append any syntax error to the tool result so local
 * models self-correct on the next turn instead of looping.
 */
import { execFileSync } from "node:child_process";
import path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

function checkCommand(filePath: string): [string, string[]] | null {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".py") return ["python3", ["-m", "py_compile", filePath]];
  if (ext === ".sh" || ext === ".bash") return ["bash", ["-n", filePath]];
  if (ext === ".json") return ["jq", ["empty", filePath]];
  return null;
}

function targetPath(input: unknown): string | null {
  if (!input || typeof input !== "object") return null;
  const obj = input as Record<string, unknown>;
  const p = obj.path ?? obj.file_path ?? obj.filePath;
  return typeof p === "string" && p.length > 0 ? p : null;
}

export default function (pi: ExtensionAPI) {
  pi.on("tool_result", async (event) => {
    if (event.isError) return;
    if (event.toolName !== "write" && event.toolName !== "edit") return;
    const fp = targetPath(event.input);
    if (!fp) return;
    const spec = checkCommand(fp);
    if (!spec) return;
    try {
      execFileSync(spec[0], spec[1], { encoding: "utf-8", timeout: 5000, stdio: "pipe" });
    } catch (err: unknown) {
      const e = err as { stderr?: string; stdout?: string; message?: string };
      const msg = (e.stderr || e.stdout || e.message || "syntax check failed").trim().slice(0, 1000);
      return {
        content: [
          ...(Array.isArray(event.content) ? event.content : []),
          { type: "text", text: `\n[syntax-check] ${spec[0]} failed on ${fp}:\n${msg}` },
        ],
      };
    }
  });
}
