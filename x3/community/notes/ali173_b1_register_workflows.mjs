// ALI-173 B1: register our two existing graphs as infinite-creation workflows (file + DB spec).
// Run: node C:/AI/community/notes/ali173_b1_register_workflows.mjs
import fs from 'node:fs';
import path from 'node:path';
import { Workflows } from 'file:///C:/AI/community/tools/infinite-creation/lib/core/db.js';

const ROOT = 'C:/AI/community/tools/infinite-creation';
const WF = path.join(ROOT, 'workflows');
const SRC = {
  h3: 'C:/AI/community/runs/ali147_pool_hc_r1_s51130001/request.api.json',
  sheet: 'C:/AI/community/runs/ali147_pool_hc_sheet_s51120000/request.api.json',
};

const H3_SPEC = {
  roles: {
    positive_prompt: { node: 'c0', field: 'prompt' },
    width: { node: 'c0', field: 'width' },
    height: { node: 'c0', field: 'height' },
    seconds: { node: 'c0', field: 'length' },
    seed: { node: 'noise', field: 'noise_seed' },
    filename_prefix: { node: 'save', field: 'filename_prefix' },
  },
  media: {
    targetNode: 'c0',
    mediaField: 'ref_images',
    typeField: '',
    loaders: { image: { class: 'LoadImage', field: 'image' }, audio: { class: 'LoadAudio', field: 'audio' }, video: { class: 'LoadVideo', field: 'file' } },
    reusePool: { image: ['img', 'sheet', 'sheet2'], audio: [], video: [] },
    maxImages: 3,
    maxAudioVideo: 0,
  },
  outputs: ['SaveVideo'],
  notes: 'ALI-147/173 H3 int8 beta6 Ref2VA two-segment graph (c0 124 f + win1 continuation). 1344x768, euler/simple, 10 steps, shift 10/3, 24 fps, audio from dec_a. Source: runs/ali147_pool_hc_r1_s51130001/request.api.json (the R1 render that passed FINAL).',
};

const SHEET_SPEC = {
  roles: {
    positive_prompt: { node: 'hc1w1pos', field: 'text' },
    negative_prompt: { node: 'hc1w1neg', field: 'text' },
    seed: { node: 'hc1w1noise', field: 'noise_seed' },
    filename_prefix: { node: 'hc1w1save', field: 'filename_prefix' },
  },
  media: {
    targetNode: 'hc1w1img',
    mediaField: 'image',
    typeField: '',
    loaders: { image: { class: 'LoadImage', field: 'image' }, audio: { class: 'LoadAudio', field: 'audio' }, video: { class: 'LoadVideo', field: 'file' } },
    reusePool: { image: ['hc1w1img', 'hc1w2img', 'hc2w1img', 'hc2w2img', 'hc3w1img', 'hc3w2img', 'hc4img', 'hc5img', 'hc6w1img', 'hc6w2img'], audio: [], video: [] },
    maxImages: 10,
    maxAudioVideo: 0,
  },
  outputs: ['SaveImage'],
  notes: 'FLUX.2 Klein 9B character-sheet builder: 10 per-woman i2i+ReferenceLatent branches (hc1w1..hc6w2) in one graph, Flux2Scheduler, one LoadImage + one SaveImage per branch. Only branch hc1w1 is role-addressable by the runner; the rest keep their baked prompts/seeds (rebuild per pick). Source: runs/ali147_pool_hc_sheet_s51120000/request.api.json.',
};

const jobs = [
  { name: 'H3 int8 Ref2VA (AlienPc R1)', kind: 'r2v', file: 'ali173_h3_int8_ref2v.json', src: SRC.h3, spec: H3_SPEC },
  { name: 'FLUX.2 Klein 9B sheet (AlienPc)', kind: 'i2i', file: 'ali173_flux2_klein9b_sheet.json', src: SRC.sheet, spec: SHEET_SPEC },
];

fs.mkdirSync(WF, { recursive: true });
for (const j of jobs) {
  const graph = fs.readFileSync(j.src, 'utf8');
  const parsed = JSON.parse(graph); // must parse as an API graph
  const nodes = Object.keys(parsed).length;
  fs.writeFileSync(path.join(WF, j.file), graph.endsWith('\n') ? graph : graph + '\n');
  const row = Workflows.upsert({ name: j.name, kind: j.kind, sourceFile: j.file, spec: j.spec, status: 'active' });
  console.log(`REGISTERED ${j.kind} "${j.name}" -> workflows/${j.file} nodes=${nodes} bytes=${Buffer.byteLength(graph)} db_id=${row.id} source_file=${row.sourceFile} status=${row.status}`);
}
console.log('WORKFLOWS NOW:', Workflows.list().map((w) => `${w.kind}:${w.name}:${w.sourceFile}`).join(' | '));
