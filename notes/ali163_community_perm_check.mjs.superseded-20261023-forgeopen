// ALI-163 community permissions check (2026-10-23). Read-only: loads the LIVE pi-permissions.jsonc via pi-permission-system's PermissionManager,
// plus the headless guard's file-tool scope, for a Forge session (cwd C:/Users/derek/5slock).
import { homedir } from "node:os";
import { join } from "node:path";
import { createRequire } from "node:module";
const npmRoot = join(process.env.APPDATA, "npm", "node_modules", "@earendil-works", "pi-coding-agent", "node_modules");
const require = createRequire(join(npmRoot, "x.js"));
const { createJiti } = require("jiti");
const piPkg = join(process.env.APPDATA, "npm", "node_modules", "@earendil-works", "pi-coding-agent");
const jiti = createJiti(import.meta.url, { interopDefault: true, alias: { "@earendil-works/pi-coding-agent": join(piPkg, "dist", "index.js") } });
const { PermissionManager } = await jiti.import(join(homedir(), ".pi", "agent", "npm", "node_modules", "pi-permission-system", "src", "permission-manager.ts"));
const guard = await jiti.import("C:/AI/director/.pi/extensions/headless-guard-and-truncate.ts");
const pm = new PermissionManager({ globalConfigPath: process.env.PERM_PATH || join(homedir(), ".pi", "agent", "pi-permissions.jsonc") });
const cwd = "C:/Users/derek/5slock";
const st = (tool, path) => pm.checkPermission(tool, { path, cwd }).state;
const H = { headless: true, cwd };
// effective = pi-permissions (external_directory then tool rule; yolo turns ask into allow) AND the guard
const eff = (tool, path) => {
  const ex = st("external_directory", path); if (ex === "deny") return "deny";
  const t = st(tool, path); if (t === "deny") return "deny";
  return guard.evaluateToolCall(tool, { path, edits: [], content: "x" }, H) ? "deny" : "allow";
};
const R = "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI";
const cases = [
  ["read", "C:/AI/director/config/llama-swap.yaml", "allow"],
  ["read", "C:/AI/strata-0.2.2/strata-swift15-iq3s.json", "allow"],
  ["grep", "C:/AI/director/scripts", "allow"],
  ["read", `${R}/custom_nodes/ComfyUI_MiniMax_H3_Extender/nodes.py`, "allow"],
  ["read", `${R}/custom_nodes/ComfyUI_MiniMax_H3_Extender/README.md`, "allow"],
  ["read", "C:/AI/community/.env", "deny"],
  ["read", "C:/AI/director/.env.local", "deny"],
  ["read", "C:/AI/director-eval/queue-verify/upstream.key", "deny"],
  ["read", "C:/Users/derek/.pi/agent/auth.json", "deny"],
  ["read", "C:/Users/derek/.pi/agent/sessions/x.jsonl", "deny"],
  ["read", "D:/Apps/finance-app/src/a.ts", "deny"],
  ["read", "C:/Apps/finance-app-rebuild/src/a.ts", "deny"],
  ["read", `${R}/main.py`, "allow"], // readfix A
  ["read", `${R}/comfy_extras/nodes_minimax_h3.py`, "allow"], // readfix A
  ["ls", `${R}/input/community/hc`, "allow"], // readfix A
  ["write", `${R}/input/community/hc/HC3_w1_face.png`, "deny"], // writes stay blocked (crops go through scripts/face_crop.py)
  ["edit", `${R}/execution.py`, "deny"],
  ["read", `${R}/.env`, "deny"],
  ["read", "C:/Users/derek/Civitai_RightFlow_Flow_2026-10-19/GROK_IMAGINE_2026-10-19b/MANIFEST.csv", "allow"], // readfix B
  ["write", "C:/Users/derek/Civitai_RightFlow_Flow_2026-10-19/x.png", "deny"],
  ["read", "C:/Users/derek/Documents/x.txt", "deny"],
  ["edit", "C:/AI/community/scripts/face_crop.py", "deny"],
  ["edit", "C:/AI/director/config/llama-swap.yaml", "deny"],
  ["write", "C:/AI/strata-0.2.2/x.json", "deny"],
  ["edit", `${R}/custom_nodes/ComfyUI_MiniMax_H3_Extender/nodes.py`, "deny"],
  ["write", "C:/AI/community/notes/x.md", "allow"],
  ["edit", "C:/AI/community/scripts/run_graph_job.py", "allow"],
  ["edit", "C:/Users/derek/5slock/ralph-community/PROMPT.md", "deny"],
  ["edit", "C:/Users/derek/5slock/ralph-community/ralph.ps1", "deny"],
];
const bcases = [
  ["python -c \"import json\np=1\nprint(p)\"", "allow"],
  ["python -c \"import os; print(os.getcwd())\"", "allow"],
  ["find C:/AI/community -name x 2>/dev/null", "allow"],
  ["python C:/AI/community/scripts/face_crop.py --src a.png --box 1,2,3,4 --out HC3_w1_face.png", "allow"],
  ["python -c \"print(1)\" && rm -rf x", "deny"],
  ["python -c \"open('C:/Users/derek/.pi/agent/pi-permissions.jsonc').read()\"", "deny"],
  ["python -c \"import urllib.request\"", "deny"],
  ["ls x; cat y", "deny"],
  ["echo x 2>/dev/null > /c/AI/x", "deny"],
];
let fail = 0;
for (const [cmd, want] of bcases) { const r = pm.checkPermission("bash", { command: cmd, cwd }); let got = r.state === "deny" ? "deny" : "allow"; if (got === "allow" && guard.evaluateToolCall("bash", { command: cmd }, H)) got = "deny"; const ok = got === want; if (!ok) fail++; console.log(`${ok ? "OK  " : "FAIL"} bash  ${got.padEnd(5)} (want ${want}) pi=${r.state} ${JSON.stringify(cmd).slice(0,90)}`); }
for (const [tool, p, want] of cases) { const got = eff(tool, p); const ok = got === want; if (!ok) fail++; console.log(`${ok ? "OK  " : "FAIL"} ${tool.padEnd(5)} ${got.padEnd(5)} (want ${want}) ${p}`); }
const N = cases.length + bcases.length; console.log(fail ? `FAILED ${fail}/${N}` : `ALL OK ${N}/${N}`);
process.exit(fail ? 1 : 0);
