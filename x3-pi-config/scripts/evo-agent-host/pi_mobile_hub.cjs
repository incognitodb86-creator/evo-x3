#!/usr/bin/env node
// pi-mobile persistent hub for the EVO-X3 (Linux port of AlienPc C:\AI\director\scripts\pi_mobile_hub.cjs, consolidation P2,
// Max Architect 2026-11-16). Runs as user evo from pi-mobile-hub.service. Keeps 127.0.0.1:<config.port> open between pi
// passes. Tailscale Serve :8444 -> this port is set once by the admin (evo is not a tailscale operator), so config.tailscale
// is false and the hub never calls `tailscale serve` itself. Read-only /media route kept (runs only, Derrick's login only).
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const HOME = os.homedir();
const PKG = path.join(HOME, '.pi/agent/npm/node_modules/pi-mobile');
const jiti = require(path.join(HOME, '.local/lib/node_modules/@earendil-works/pi-coding-agent/node_modules/jiti'))(__dirname);
const { Hub, snapshotWeb } = jiti(path.join(PKG, 'src/hub.ts'));
const { loadConfig, linkSecret } = jiti(path.join(PKG, 'src/store.ts'));
const { createMediaHandler } = require(path.join(__dirname, 'pi_mobile_media.cjs'));

const config = loadConfig();
const secret = linkSecret();
if (!config.enabled) { console.log('[pi-mobile] config.enabled is false; exiting.'); process.exit(0); }
const webDir = path.join(__dirname, 'pi_mobile_web_staged');
const web = fs.existsSync(path.join(webDir, 'app.js')) ? snapshotWeb(webDir) : undefined;
const hub = new Hub({ config: { ...config, tailscale: false }, web, secret, serve: undefined });

const media = createMediaHandler({ roots: [path.join(HOME, 'AI/community/runs')], allowedLogin: 'derek.boone86@gmail.com' });
const srv = hub.server;
const orig = srv.listeners('request');
srv.removeAllListeners('request');
srv.on('request', (req, res) => {
  try { if (media(req, res)) return; } catch (e) { if (!res.headersSent) { res.writeHead(500); res.end(); } return; }
  for (const l of orig) l.call(srv, req, res);
});
const keepAliveTimer = setInterval(() => {}, 60000);
function shutdown() { console.log('[pi-mobile] Shutting down hub...'); clearInterval(keepAliveTimer); try { hub.close(); } catch (e) {} process.exit(0); }
process.on('SIGINT', shutdown); process.on('SIGTERM', shutdown);
hub.listen().then(() => console.log(`[pi-mobile] Persistent hub listening on 127.0.0.1:${hub.port}`))
  .catch((err) => { console.error('[pi-mobile] Failed to start hub:', err); process.exit(1); });
