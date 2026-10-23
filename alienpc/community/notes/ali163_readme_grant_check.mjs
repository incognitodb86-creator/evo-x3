// ALI-163 README grant check (2026-10-23). Read-only: loads the LIVE pi-permissions.jsonc via pi-permission-system's PermissionManager.
import { homedir } from "node:os";
import { join } from "node:path";
import { createRequire } from "node:module";
const npmRoot = join(process.env.APPDATA, "npm", "node_modules", "@earendil-works", "pi-coding-agent", "node_modules");
const require = createRequire(join(npmRoot, "x.js"));
const { createJiti } = require("jiti");
const piPkg = join(process.env.APPDATA, "npm", "node_modules", "@earendil-works", "pi-coding-agent");
const jiti = createJiti(import.meta.url, { interopDefault: true, alias: { "@earendil-works/pi-coding-agent": join(piPkg, "dist", "index.js") } });
const { PermissionManager } = await jiti.import(join(homedir(), ".pi", "agent", "npm", "node_modules", "pi-permission-system", "src", "permission-manager.ts"));
const pm = new PermissionManager({ globalConfigPath: join(homedir(), ".pi", "agent", "pi-permissions.jsonc") });
const cwd = "C:/Users/derek/5slock";
const st = (tool, path) => pm.checkPermission(tool, { path, cwd }).state;
const R = "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI";
const cases = [
  [`${R}/custom_nodes/ComfyUI_MiniMax_H3_Extender/README.md`, "allow"],
  [`${R}/custom_nodes/ComfyUI-GGUF/tools/README.md`, "allow"],
  [`${R}/custom_nodes/ComfyUI_MiniMax_H3_Extender/__init__.py`, "deny"],
  [`${R}/custom_nodes/ComfyUI_MiniMax_H3_Extender/nodes.md`, "deny"],
  [`${R}/main.py`, "deny"],
  [`${R}/user/default/comfy.settings.json`, "deny"],
  [`${R}/custom_nodes/x/README_dir/secret.md`, "deny"],
];
let fail = 0;
for (const [p, want] of cases) { const ext = st("external_directory", p); const ok = ext === want; if (!ok) fail++; console.log(`${ok ? "OK  " : "FAIL"} external_directory ${ext.padEnd(5)} (want ${want}) ${p}`); }
const ex = `${R}/custom_nodes/ComfyUI_MiniMax_H3_Extender/README.md`;
for (const [tool, want] of [["read", "allow"], ["grep", "allow"], ["edit", "deny"], ["write", "deny"]]) { const s = st(tool, ex); const ok = s === want; if (!ok) fail++; console.log(`${ok ? "OK  " : "FAIL"} ${tool.padEnd(5)} ${s} (want ${want}) Extender README`); }
console.log(fail ? `FAILED ${fail}` : "ALL OK");
process.exit(fail ? 1 : 0);
