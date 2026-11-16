// Node 22+ strip-types import of loop-guard.ts helpers
import { tokenizeCmd, runDirFromCmd, normalizeRunDir, parodyRunKey } from './loop-guard.ts';
import process from 'node:process';

const cases = [
  ['submit_parody_run.py writer-run /home/evo/AI/community/runs/clip1 --ask hi', '/home/evo/AI/community/runs/clip1'],
  ['submit_parody_run.py --ask hi --run-dir /home/evo/AI/community/runs/clip2 writer-run', '/home/evo/AI/community/runs/clip2'],
  ['/venv/bin/python3 render_writer_pipeline.py --position doggy "/home/evo/AI/community/runs/Clip3"', '/home/evo/AI/community/runs/Clip3'],
  ['render_writer_pipeline.py --run-dir=/tmp/R4 --ask x', '/tmp/R4'],
  ['submit_parody_run.py writer-run --still /tmp/a.jpg /tmp/R5', '/tmp/R5'],
  ['submit_parody_run.py writer-run --continued /tmp/R6 --ask x', '/tmp/R6'],
];
let fail = 0;
for (const [cmd, expect] of cases) {
  const got = runDirFromCmd(cmd);
  if (got !== expect) { console.error('FAIL runDir', cmd, 'got', got, 'want', expect); fail++; }
  const key = parodyRunKey({ command: cmd });
  if (key !== 'parody::' + expect) { console.error('FAIL key', cmd, key); fail++; }
}
// Linux must keep case
if (process.platform !== 'win32') {
  if (normalizeRunDir('/tmp/ClipA') !== '/tmp/ClipA') { console.error('FAIL case'); fail++; }
  if (parodyRunKey({ command: 'submit_parody_run.py writer-run /tmp/ClipA' }) ===
      parodyRunKey({ command: 'submit_parody_run.py writer-run /tmp/clipa' })) {
    console.error('FAIL linux case collapse'); fail++;
  }
}
if (tokenizeCmd("run 'a b' c").join('|') !== 'run|a b|c') { console.error('FAIL tokenize'); fail++; }
if (fail) { console.error(fail, 'failed'); process.exit(1); }
console.log('loop-guard unit tests OK', cases.length + 2);
