// node test/prompt-cache-incremental.test.js — incremental prompt-cache persistence
// (createIncrementalPersister + fetchConversationAssetMetadata onConversation / 429 retry). No network, no timers.
const assert = require('assert');
const GA = require('../src/grok-assets.js');
const GU = require('../src/utils.js');

const convRows = (cid) => ({ responses: [{ fileAttachmentAssetMetadata: [
  { assetId: cid + '-img', mediaGenInput: { textToImage: { prompt: 'p-' + cid } }, mimeType: 'image/jpeg' },
  { assetId: cid + '-vid', mediaGenInput: { imageToVideo: { prompt: '', inputAssets: [cid + '-img'] } }, mimeType: 'video/mp4' }] }] });
function mockFetch({ fail429 = {} } = {}) {
  const calls = []; const left = { ...fail429 };
  const f = async (url) => {
    const cid = decodeURIComponent(url.split('/conversations/')[1].split('/')[0]); calls.push(cid);
    if (left[cid] > 0) { left[cid]--; return { ok: false, status: 429, headers: { get: (h) => (h === 'Retry-After' ? '7' : null) } }; }
    return { ok: true, json: async () => convRows(cid) };
  };
  f.calls = calls; return f;
}

(async () => {
  // 1) persister: flushes every N ticks, on elapsed time, and on finish
  let t = 0; let flushed = 0;
  const p = GA.createIncrementalPersister({ flushEvery: 3, flushIntervalMs: 1000, now: () => t, flush: async () => { flushed++; } });
  await p.tick(); await p.tick(); assert.strictEqual(flushed, 0);
  await p.tick(); assert.strictEqual(flushed, 1, 'flush at N=3');
  t = 1500; await p.tick(); assert.strictEqual(flushed, 2, 'flush on interval');
  await p.finish(); assert.strictEqual(flushed, 2, 'nothing pending -> no flush');
  await p.tick(); await p.finish(); assert.strictEqual(flushed, 3, 'finish flushes pending');
  console.log('PASS 1: persister flushes by count, interval and finish');

  // 2) onConversation per successful conversation; persisted "store" grows incrementally
  const store = { e: {}, done: {} }; const snapshots = [];
  const persister = GA.createIncrementalPersister({ flushEvery: 2, flushIntervalMs: 1e9, now: () => 0,
    flush: async () => snapshots.push(Object.keys(store.e).length) });
  const cids = ['c1', 'c2', 'c3', 'c4', 'c5'];
  let r = await GA.fetchConversationAssetMetadata(mockFetch(), cids, { sleepImpl: async () => {}, randomImpl: () => 0,
    onConversation: async (cid, entries) => { entries.forEach((e, id) => { store.e[id] = e.prompt; }); store.done[cid] = 1; await persister.tick(); } });
  await persister.finish();
  assert.strictEqual(r.conversationsFetched, 5);
  assert.deepStrictEqual(snapshots, [4, 8, 10], 'flushed after conv 2, 4 and on finish');
  assert.strictEqual(store.e['c3-img'], 'p-c3');
  console.log('PASS 2: onConversation persists every conversation, flushes incrementally');

  // 3) next run skips conversations already done (caller-side filter, as content.js does)
  const todo = [...cids, 'c6'].filter((c) => !store.done[c]);
  const f3 = mockFetch();
  r = await GA.fetchConversationAssetMetadata(f3, todo, { sleepImpl: async () => {} });
  assert.deepStrictEqual(f3.calls, ['c6'], 'only the new conversation is fetched');
  console.log('PASS 3: already-fetched conversations skipped on resume');

  // 4) 429 retried with backoff honoring Retry-After; recovered, not counted as error
  const sleeps = [];
  const f4 = mockFetch({ fail429: { c2: 2 } });
  r = await GA.fetchConversationAssetMetadata(f4, ['c1', 'c2'], { sleepImpl: async (ms) => { sleeps.push(ms); },
    randomImpl: () => 0, maxRetries: 5, retryBaseMs: 2000, retryMaxMs: 30000, throttleMs: 600 });
  assert.strictEqual(r.errors, 0); assert.strictEqual(r.conversationsFetched, 2);
  assert.deepStrictEqual(f4.calls, ['c1', 'c2', 'c2', 'c2']);
  assert.ok(sleeps.includes(7000), 'Retry-After 7s honored: ' + sleeps);
  console.log('PASS 4: 429 retried with Retry-After backoff');

  // 5) abort mid-walk: conversations done before the abort were already handed to onConversation
  const seen = []; let n = 0;
  r = await GA.fetchConversationAssetMetadata(mockFetch(), cids, { sleepImpl: async () => {},
    signalAborted: () => n >= 2, onConversation: async (cid) => { seen.push(cid); n++; } });
  assert.strictEqual(r.aborted, true); assert.deepStrictEqual(seen, ['c1', 'c2']);
  console.log('PASS 5: cancel keeps already-persisted conversations');

  // 6) cache cap holds a ~32k library without evicting
  const big = { v: 1, e: {} }; for (let i = 0; i < 32000; i++) big.e['a' + i] = { p: 'x', s: null, t: i };
  assert.strictEqual(Object.keys(GU.prunePromptCacheStore(big).e).length, 32000);
  console.log('PASS 6: 32k-entry cache not pruned');
  // 7) getAssetsByIds retries a 429 batch instead of dropping it
  let hits = 0;
  const fb = async (url) => { const ids = new URL(url).searchParams.getAll('assetIds'); hits++;
    if (hits === 2) return { ok: false, status: 429, headers: { get: () => '3' } };
    return { ok: true, json: async () => ({ assets: ids.map((id) => ({ assetId: id, mimeType: 'image/jpeg' })) }) }; };
  const ids = Array.from({ length: 120 }, (_, i) => 'id' + i);
  const rb = await GA.getAssetsByIds(fb, ids, { sleepImpl: async () => {} });
  assert.strictEqual(rb.errors, 0); assert.strictEqual(rb.assets.length, 120); assert.strictEqual(rb.missingIds.length, 0);
  console.log('PASS 7: getAssetsByIds retries 429 batches (no silent loss)');
  console.log('ALL TESTS PASSED');
})().catch((e) => { console.error('FAIL', e); process.exit(1); });
