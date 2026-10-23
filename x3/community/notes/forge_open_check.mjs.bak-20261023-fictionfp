// forgeopen check (2026-10-23, ALI-163): loads the Forge-only pi policy via pi-permission-system's PermissionManager plus the headless guard
// in open mode for a Forge session (cwd C:/Users/derek/5slock). Secrets must be denied; finance app + a sample of everything else must pass.
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
const pp = await jiti.import("C:/AI/director/.pi/extensions/protected-paths.ts");
const policy = process.env.FORGE_POLICY || join(homedir(), ".pi", "forge-policy", "pi-permissions.jsonc");
const pm = new PermissionManager({ globalConfigPath: policy });
const cwd = "C:/Users/derek/5slock";
const H = { headless: true, cwd };
const eff = (tool, x) => {
  const isCmd = tool === "bash" || tool === "powershell";
  const r = pm.checkPermission(tool, isCmd ? { command: x, cwd } : { path: x, cwd });
  if (r.state === "deny") return "deny(pi)";
  const ppv = !pp.forgeOpenCwd(cwd) && pp.evaluate(tool, isCmd ? { command: x } : { path: x }, cwd);
  if (ppv) return "deny(protected-paths)";
  const v = guard.evaluateToolCall(tool, isCmd ? { command: x } : { path: x, edits: [], content: "x" }, H);
  return v ? `deny(${v.id})` : "allow";
};
const cases = [
  // secrets: denied
  ["read", "D:/Apps/finance-app/.env", "deny"], ["read", "C:/Apps/finance-app-rebuild/.env.local", "deny"], ["read", "C:/AI/director/.env", "deny"],
  ["read", "C:/Users/derek/AppData/Roaming/rclone/rclone.conf", "deny"], ["read", "C:/Users/derek/.pi/agent/auth.json", "deny"],
  ["read", "C:/AI/director-eval/queue-verify/upstream.key", "deny"], ["read", "C:/Users/derek/.ssh/id_ed25519", "deny"], ["grep", "C:/AI/community/hf_token.txt", "deny"],
  ["edit", "D:/Apps/finance-app/.env", "deny"],
  ["bash", "cat D:/Apps/finance-app/.env", "deny"], ["powershell", "Get-Content C:\\Apps\\finance-app-rebuild\\.env", "deny"], ["bash", "rclone config show", "deny"],
  ["powershell", "echo $env:PLAID_SECRET", "deny"], ["bash", "printenv", "deny"], ["powershell", "cmdkey /list", "deny"],
  // finance app: allowed
  ["read", "D:/Apps/finance-app/src/server/ledger.ts", "allow"], ["write", "D:/Apps/finance-app/src/finance_note.md", "allow"],
  ["edit", "C:/Apps/finance-app-rebuild/src/a.ts", "allow"], ["bash", "curl -s http://127.0.0.1:3100/api/health", "allow"],
  ["powershell", "Get-ChildItem D:\\Apps\\finance-app\\src", "allow"],
  // everything else: allowed (sample)
  ["read", "C:/Users/derek/Documents/x.txt", "allow"], ["read", "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/execution.py", "allow"],
  ["write", "C:/Users/derek/5slock/approved_characters/x.png", "allow"], ["edit", "C:/AI/director/.pi/extensions/headless-guard-and-truncate.ts", "allow"],
  ["write", "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/user/default/x.json", "allow"], ["edit", "C:/Users/derek/5slock/ralph-community/ralph.ps1", "allow"],
  ["bash", "git push origin main", "allow"], ["bash", "rm -rf C:/AI/community/tmp/x; ls && echo done", "allow"], ["bash", "pip install insightface", "allow"],
  ["bash", "python -c \"import os\nprint(os.getcwd())\" 2>/dev/null", "allow"], ["bash", "find C:/Users/derek -maxdepth 3 -iname \"*h3*\" 2>/dev/null | head", "allow"],
  ["powershell", "Stop-Process -Name foo -ErrorAction SilentlyContinue; Invoke-WebRequest https://example.com -OutFile C:\\AI\\community\\tmp\\x.html", "allow"],
  ["bash", "curl -s http://127.0.0.1:8080/upstream/x/v1/models", "allow"],
  ["edit", "C:/AI/community/scripts/face_crop.py", "allow"], ["edit", "C:/AI/community/scripts/comm.py", "deny"], ["bash", "echo x > C:/AI/community/scripts/comm.py", "deny"],
  // R4G regression: the 12 commands/paths denied 1:17-1:38 PM CT must now pass
  ["bash", "wc -l C:/Users/derek/5slock/ralph-community/TASKS.md; awk 'NR>=1 && NR<=20 {print NR\": \"length($0)}' C:/Users/derek/5slock/ralph-community/TASKS.md", "allow"],
  ["bash", "python -c \"\nimport json\np=r'C:\\AI\\community\\runs\\ali147_pool_hc_c1_s51100001\\request.api.json'\ng=json.loads(open(p,encoding='utf-8').read())\nprint('nodes',len(g))\n\"", "allow"],
  ["bash", "grep -rn \"Unknown input\\|not in node_inputs\\|extra_inputs\\|hidden_inputs\" C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/execution.py | head -20", "allow"],
  ["grep", "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/execution.py", "allow"],
  ["bash", "find C:/Users/derek -maxdepth 5 -iname \"*MiniMax*H3*\" -type d 2>/dev/null", "allow"],
  ["find", "C:/Users/derek", "allow"],
  ["bash", "python -c \"p=r'C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/comfy_extras/nodes_minimax_h3.py';L=open(p,encoding='utf-8').read().splitlines();print(len(L))\"", "allow"],
  ["grep", "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/comfy_extras/nodes_minimax_h3.py", "allow"],
  ["bash", "python -c \"\nimport re\np = r'C:/AI/community/notes/hc_prompt_face_audit_20261023.md'\nt = open(p, encoding='utf-8').read()\nprint('bytes', len(t.encode('utf-8')))\n\"", "allow"],
  ["read", "C:/Users/derek/Civitai_RightFlow_Flow_2026-10-19/GROK_IMAGINE_2026-10-19b/MANIFEST.csv", "allow"],
  ["bash", "python -c \"import os; d=r'C:/Users/derek'; print([n for n in sorted(os.listdir(d)) if 'ow' in n or 'ivit' in n.lower()][:40])\"", "allow"],
  ["ls", "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/hc", "allow"],
];
let fail = 0;
for (const [tool, x, want] of cases) { const got = eff(tool, x); const ok = got.startsWith(want); if (!ok) fail++; console.log(`${ok ? "OK  " : "FAIL"} ${tool.padEnd(10)} ${got.padEnd(22)} (want ${want}) ${JSON.stringify(x).slice(0, 110)}`); }
console.log(fail ? `FAILED ${fail}/${cases.length}` : `ALL OK ${cases.length}/${cases.length}`);
process.exit(fail ? 1 : 0);
