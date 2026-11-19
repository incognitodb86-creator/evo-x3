'use strict';
// Read-only /media route for the pi-mobile hub (plan 2026-10-30-pi-media-to-phone-local-plan, PM-1/2/3/7).
// Copied verbatim from AlienPc C:\AI\director\scripts\pi_mobile_media.cjs for the EVO-X3 hub (consolidation P2, 2026-11-16).
// Serves only .mp4/.jpg from allowed roots, only to Derrick's Tailscale login, with Range support.
const fs = require('node:fs');
const path = require('node:path');

const TYPES = { '.mp4': 'video/mp4', '.jpg': 'image/jpeg' };
// PM-3 denied roots (plan) + Sydney folders (brief: denied too).
const DENIED = /(sydney|imagine|grok|family|approved_characters)/i;

function norm(p) { return process.platform === 'win32' ? p.toLowerCase() : p; }

function createMediaHandler(opts) {
  const allowedLogin = String(opts.allowedLogin || '').trim().toLowerCase();
  const roots = (opts.roots || []).map((r) => fs.realpathSync.native(r));
  if (!allowedLogin) throw new Error('allowedLogin required');
  if (!roots.length) throw new Error('at least one root required');

  function fail(res, code, msg) {
    res.writeHead(code, { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff' });
    res.end(msg + '\n');
    return true;
  }

  return function media(req, res) {
    const rawUrl = req.url || '/';
    const raw = rawUrl.split('?')[0];
    if (raw !== '/media' && !raw.startsWith('/media/')) return false;
    if (req.method !== 'GET' && req.method !== 'HEAD') return fail(res, 405, 'method not allowed');
    // PM-2 identity gate: Tailscale serve adds Tailscale-User-Login for user nodes; tagged nodes have none.
    const login = String(req.headers['tailscale-user-login'] || '').trim().toLowerCase();
    if (!login || login !== allowedLogin) return fail(res, 403, 'forbidden');
    // PM-1 containment.
    if (/\\|%5c/i.test(raw)) return fail(res, 400, 'bad path');
    let dec;
    try { dec = decodeURIComponent(raw); } catch { return fail(res, 400, 'bad path'); }
    if (dec.includes('%') || dec.includes('\\') || dec.includes(':') || dec.includes('\0')) return fail(res, 400, 'bad path');
    const rel = dec.slice('/media/'.length);
    const segs = rel.split('/');
    if (!rel || segs.some((s) => s === '' || s === '.' || s === '..' || /^\.+$/.test(s))) return fail(res, 400, 'bad path');
    // PM-3 content scope.
    if (segs.some((s) => DENIED.test(s))) return fail(res, 403, 'forbidden');
    const ext = path.extname(segs[segs.length - 1]).toLowerCase();
    const type = TYPES[ext];
    if (!type) return fail(res, 403, 'forbidden');
    let real = null, root = null;
    for (const r of roots) {
      let p;
      try { p = fs.realpathSync.native(path.join(r, ...segs)); } catch { continue; }
      root = r; real = p; break;
    }
    if (!real) return fail(res, 404, 'not found');
    const rootN = norm(root).replace(/[\\/]+$/, '') + path.sep;
    if (!norm(real).startsWith(rootN)) return fail(res, 403, 'forbidden');
    if (path.relative(root, real).split(/[\\/]/).some((s) => DENIED.test(s))) return fail(res, 403, 'forbidden');
    if (!TYPES[path.extname(real).toLowerCase()]) return fail(res, 403, 'forbidden');
    let st;
    try { st = fs.statSync(real); } catch { return fail(res, 404, 'not found'); }
    if (!st.isFile()) return fail(res, 404, 'not found');
    const size = st.size;
    const base = { 'content-type': type, 'accept-ranges': 'bytes', 'cache-control': 'private, no-store', 'x-content-type-options': 'nosniff', 'referrer-policy': 'no-referrer' };
    // PM-7 Range.
    const range = req.headers.range;
    let start = 0, end = size - 1, status = 200;
    if (range) {
      const m = /^bytes=(\d*)-(\d*)$/.exec(String(range).trim());
      if (!m || (m[1] === '' && m[2] === '')) { res.writeHead(416, { ...base, 'content-range': `bytes */${size}` }); res.end(); return true; }
      if (m[1] === '') { const n = Number(m[2]); start = Math.max(0, size - n); }
      else { start = Number(m[1]); if (m[2] !== '') end = Math.min(Number(m[2]), size - 1); }
      if (start >= size || start > end) { res.writeHead(416, { ...base, 'content-range': `bytes */${size}` }); res.end(); return true; }
      status = 206; base['content-range'] = `bytes ${start}-${end}/${size}`;
    }
    res.writeHead(status, { ...base, 'content-length': String(end - start + 1) });
    if (req.method === 'HEAD' || size === 0) { res.end(); return true; }
    const s = fs.createReadStream(real, { start, end });
    s.on('error', () => res.destroy());
    s.pipe(res);
    return true;
  };
}

module.exports = { createMediaHandler, DENIED };
