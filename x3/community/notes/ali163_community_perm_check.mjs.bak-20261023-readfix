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
const pm = new PermissionManager({ globalConfigPath: join(homedir(), ".pi", "agent", "pi-permissions.jsonc") });
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
  ["read", `${R}/main.py`, "deny"],
  ["edit", "C:/AI/director/config/llama-swap.yaml", "deny"],
  ["write", "C:/AI/strata-0.2.2/x.json", "deny"],
  ["edit", `${R}/custom_nodes/ComfyUI_MiniMax_H3_Extender/nodes.py`, "deny"],
  ["write", "C:/AI/community/notes/x.md", "allow"],
  ["edit", "C:/AI/community/scripts/run_graph_job.py", "allow"],
  ["edit", "C:/Users/derek/5slock/ralph-community/PROMPT.md", "deny"],
  ["edit", "C:/Users/derek/5slock/ralph-community/ralph.ps1", "deny"],
];
let fail = 0;
for (const [tool, p, want] of cases) { const got = eff(tool, p); const ok = got === want; if (!ok) fail++; console.log(`${ok ? "OK  " : "FAIL"} ${tool.padEnd(5)} ${got.padEnd(5)} (want ${want}) ${p}`); }
console.log(fail ? `FAILED ${fail}/${cases.length}` : `ALL OK ${cases.length}/${cases.length}`);
process.exit(fail ? 1 : 0);
