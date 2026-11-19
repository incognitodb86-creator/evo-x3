// Tests for evo-git-safety.mjs. Run: node --test .github/hooks/scripts/evo-git-safety.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { main, runHook, NO_DECISION } from './evo-git-safety.mjs';

const cli = (toolName, toolArgs) => main(JSON.stringify({ toolName, toolArgs: JSON.stringify(toolArgs), cwd: 'C:\\repo' }));
const vsc = (tool_name, tool_input) => main(JSON.stringify({ hook_event_name: 'PreToolUse', tool_name, tool_input, cwd: '/repo' }));
const sh = (command) => cli('powershell', { command, description: 'x' });
const verdict = (out) => out.permissionDecision ?? 'none';

const DENY = [
  'git push --force origin u58',
  'git push -f origin u58',
  'git push --force-with-lease',
  'git -C "C:\\Users\\Derek.Boone\\Desktop\\evo-x3" push origin +u58',
  'git push origin :old-branch',
  'git push --delete origin x',
  'git push --mirror gitea',
  'git add -A',
  'git add .',
  'git add -u',
  'git add -f records/notes.md',
  'git add --all records',
  'git status; git add .',
  'git commit -am "wip"',
  'git commit --all -m wip',
  'git commit -n -m wip',
  'git commit --no-verify -m wip',
  'git -c core.hooksPath=/dev/null commit -m wip',
  'git filter-repo --force --to-subdirectory-filter x3/render/',
  'git filter-branch --tree-filter true HEAD',
  'git sparse-checkout disable',
  'git sparse-checkout add hosts/x3/live',
  'git sparse-checkout add "hosts/x3/live/systemd"',
  'git sparse-checkout set hosts .github',
  'git sparse-checkout add hosts\\x3\\',
  'git sparse-checkout init --no-cone',
  'Get-Content C:\\Users\\me\\.ssh\\id_ed25519',
  'cat ~/.pi/agent/auth.json',
  'type config\\pi\\mcp.json',
  'Copy-Item C:\\x\\models.json C:\\tmp\\',
  'cat /etc/evo-x3/llm.env',
  'Get-Content .env.local',
  'git add records/backup/auth.json',
  '',
];

const ASK = [
  'git reset --hard HEAD~1',
  'git clean -fd',
  'git rebase -i HEAD~3',
];

const ALLOW = [
  'git push origin u58',
  'git -c credential.helper= -c "credential.helper=!gh auth git-credential" push origin mono',
  'git -C C:\\tmp\\mono-build\\x3-render filter-repo --to-subdirectory-filter x3/render/',
  'git filter-repo --version',
  'git add .github/copilot-instructions.md records/x/PLAN.md',
  'git add --sparse .github/agents/evo-planner.agent.md',
  'git commit -m "push the fix and add -A later"',
  'git commit --amend -m "fix typo"',
  'git status --porcelain=v1 -uall',
  'git sparse-checkout add .github',
  'git sparse-checkout list',
  "git ls-files --cached -- '**/auth.json' '**/mcp.json' '*.env'",
  'git rm --cached records/gufo/home-evo-pi-panes-forge/mcp.json',
  'Get-Content config\\pi\\models.json.example',
  'Get-Content config\\pi-evo\\.env.example',
  'git --no-pager log --oneline -5',
  'git reset HEAD records/x.md',
  'Get-Command git',
  'node --test .github/hooks/scripts/',
];

for (const command of DENY) {
  test(`deny: ${command || '(empty command)'}`, () => assert.equal(verdict(sh(command)), 'deny'));
}
for (const command of ASK) {
  test(`ask: ${command}`, () => assert.equal(verdict(sh(command)), 'ask'));
}
for (const command of ALLOW) {
  test(`allow: ${command}`, () => assert.deepEqual(sh(command), NO_DECISION));
}

test('VS Code payload: Bash force push is denied', () => {
  assert.equal(verdict(vsc('Bash', { command: 'git push --force' })), 'deny');
});
test('VS Code payload: Read of a secret file is denied', () => {
  assert.equal(verdict(vsc('Read', { file_path: '/home/evo/.pi/agent/auth.json' })), 'deny');
});
test('CLI payload: view of a secret file is denied', () => {
  assert.equal(verdict(cli('view', { path: 'C:\\Users\\me\\.ssh\\config' })), 'deny');
});
test('CLI payload: grep over a secret file is denied', () => {
  assert.equal(verdict(cli('grep', { pattern: 'x', paths: ['C:\\x\\mcp.json'] })), 'deny');
});
test('view of a normal file has no decision', () => {
  assert.deepEqual(cli('view', { path: 'C:\\repo\\README.md' }), NO_DECISION);
});
test('non-shell tools have no decision', () => {
  assert.deepEqual(cli('read_powershell', { shellId: '1', delay: 5 }), NO_DECISION);
  assert.deepEqual(cli('task', { prompt: 'git push --force' }), NO_DECISION);
});
test('unreadable toolArgs are denied', () => {
  assert.equal(verdict(main(JSON.stringify({ toolName: 'bash', toolArgs: '{not json' }))), 'deny');
});
test('non-JSON input has no decision', () => {
  assert.deepEqual(main('not json'), NO_DECISION);
  assert.deepEqual(main(''), NO_DECISION);
});
test('internal errors fail closed', () => {
  const out = runHook(() => { throw new Error('boom'); });
  assert.equal(out.permissionDecision, 'deny');
  assert.equal(out.hookSpecificOutput.permissionDecision, 'deny');
});
test('deny output carries both CLI and VS Code shapes', () => {
  const out = sh('git push --force');
  assert.equal(out.hookSpecificOutput.hookEventName, 'PreToolUse');
  assert.equal(out.hookSpecificOutput.permissionDecision, 'deny');
  assert.match(out.permissionDecisionReason, /^EVO git-safety:/);
});
test('script run as a process prints exactly one JSON object and exits 0', () => {
  const script = fileURLToPath(new URL('./evo-git-safety.mjs', import.meta.url));
  const input = JSON.stringify({ toolName: 'powershell', toolArgs: { command: 'git add -A' } });
  const run = spawnSync(process.execPath, [script], { input, encoding: 'utf8' });
  assert.equal(run.status, 0);
  assert.equal(JSON.parse(run.stdout.trim()).permissionDecision, 'deny');
});
