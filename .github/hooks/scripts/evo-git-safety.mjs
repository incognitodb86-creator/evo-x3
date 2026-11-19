// EVO git-safety guard: PreToolUse hook registered by .github/hooks/evo-git-safety.json.
//
// Denies this repo's never-rules: force or delete pushes, broad staging (`git add -A|.|-u|-f`,
// `commit -a`), hook bypass, `filter-branch` and `filter-repo --force`, sparse-checkout changes that
// would check out hosts/x3/live/systemd (Windows-invalid names), and reads of secret files. Plain
// pushes are allowed (Derrick 2026-11-19: GitHub first, Max mirrors to Gitea). Asks before
// `reset --hard`, `clean -f` or `rebase`.
//
// Accepts both payload shapes: camelCase `preToolUse` (toolName/toolArgs, runtime tool names) and
// VS Code-style `PreToolUse` (tool_name/tool_input, Claude tool names such as Bash and Read).
//
// NOT A SECURITY BOUNDARY: it matches command text, so a command built at run time can dodge it.
// It never executes or interpolates tool input, never returns "allow", and fails closed: any
// internal error denies the call.

import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

export const NO_DECISION = Object.freeze({ continue: true });

const SHELL_TOOLS = new Set(['powershell', 'bash', 'shell', 'run_in_terminal', 'send_to_terminal']);
const PATH_TOOLS = new Set(['view', 'read', 'read_file', 'grep', 'rg']);
const PATH_KEYS = ['path', 'paths', 'filePath', 'file_path'];
const MAX_COMMAND_CHARS = 256 * 1024;

const SECRET_PATTERNS = [
  /(^|[\\/])(auth|mcp|models|models-store)\.json$/i,
  /(^|[\\/])\.env(\.(?!example$)[^\\/]+)?$/i,
  /[^\\/]\.env$/i,
  /\.(token|cred|pem)$/i,
  /(^|[\\/])id_(rsa|ed25519|ecdsa|dsa)$/i,
  /(^|[\\/])\.ssh([\\/]|$)/i,
  /^\/etc\/evo-x3(\/|$)/i,
];
// git subcommands that only handle file names, never contents.
const NAME_ONLY_GIT = new Set(['ls-files', 'check-ignore', 'status', 'rm']);
const SYSTEMD_CONE = ['hosts', 'hosts/x3', 'hosts/x3/live', 'hosts/x3/live/systemd'];
const GIT_OPTS_WITH_VALUE = new Set(['-c', '-C', '--git-dir', '--work-tree', '--namespace', '--exec-path']);

function decision(permissionDecision, reason) {
  const permissionDecisionReason = `EVO git-safety: ${reason}`;
  return {
    permissionDecision,
    permissionDecisionReason,
    hookSpecificOutput: { hookEventName: 'PreToolUse', permissionDecision, permissionDecisionReason },
  };
}
const deny = (reason) => decision('deny', reason);
const ask = (reason) => decision('ask', reason);

export function isSecretPath(value) {
  if (typeof value !== 'string') return false;
  const text = value.trim().replace(/^['"]|['"]$/g, '');
  return text !== '' && SECRET_PATTERNS.some((re) => re.test(text));
}

// Splits shell text into command segments of unquoted tokens. Separators outside quotes:
// ; | & newline ( ) { }. Good enough for matching; not a real shell parser.
export function segments(text) {
  const out = [];
  let tokens = [];
  let token = '';
  let quote = null;
  let inToken = false;
  const endToken = () => {
    if (inToken) tokens.push(token);
    token = '';
    inToken = false;
  };
  const endSegment = () => {
    endToken();
    if (tokens.length) out.push(tokens);
    tokens = [];
  };
  for (const ch of text) {
    if (quote) {
      if (ch === quote) quote = null;
      else token += ch;
      continue;
    }
    if (ch === '"' || ch === "'") {
      quote = ch;
      inToken = true;
    } else if (';|&\n\r(){}'.includes(ch)) {
      endSegment();
    } else if (/\s/.test(ch)) {
      endToken();
    } else {
      token += ch;
      inToken = true;
    }
  }
  endSegment();
  return out;
}

function parseGit(tokens) {
  const at = tokens.findIndex((t) => /^(?:.*[\\/])?git(?:\.exe)?$/i.test(t));
  if (at < 0) return null;
  const globals = [];
  let j = at + 1;
  while (j < tokens.length && tokens[j].startsWith('-')) {
    if (GIT_OPTS_WITH_VALUE.has(tokens[j])) {
      globals.push(tokens[j], tokens[j + 1] ?? '');
      j += 2;
    } else {
      globals.push(tokens[j]);
      j += 1;
    }
  }
  if (j >= tokens.length) return null;
  return { sub: tokens[j].toLowerCase(), args: tokens.slice(j + 1), globals };
}

const shortCluster = (arg) => /^-[a-zA-Z]+$/.test(arg);
const hasShort = (args, letter) => args.some((a) => shortCluster(a) && a.slice(1).includes(letter));
const normPath = (p) => p.replace(/\\/g, '/').replace(/^\.\//, '').replace(/\/+$/, '').toLowerCase();

export function classifyGit({ sub, args, globals }) {
  for (let i = 0; i < globals.length; i += 1) {
    if (globals[i] === '-c' && /^core\.hookspath=/i.test(globals[i + 1] ?? '')) {
      return deny('git -c core.hooksPath bypasses git hooks.');
    }
  }
  if (args.includes('--no-verify')) return deny('--no-verify bypasses git hooks.');

  switch (sub) {
    case 'push': {
      const forced = args.some((a) => /^--(force|force-with-lease|force-if-includes|mirror|delete|prune)(=|$)/.test(a))
        || hasShort(args, 'f') || hasShort(args, 'd')
        || args.some((a) => !a.startsWith('-') && /^[+:]/.test(a));
      if (forced) return deny('force, delete or mirror push. Never from an agent; give Derrick the exact command.');
      return null;
    }
    case 'add': {
      const broad = args.some((a) => ['.', './', ':/', ':', '*', '--all', '--update', '--force', '--no-ignore-removal'].includes(a))
        || hasShort(args, 'A') || hasShort(args, 'u') || hasShort(args, 'f');
      if (broad) return deny('broad or forced staging. Add files by explicit path only (no -A, ., -u, -f).');
      return null;
    }
    case 'commit':
      if (args.includes('--all') || hasShort(args, 'a')) return deny('commit -a stages everything. Add files by explicit path, then commit.');
      if (hasShort(args, 'n')) return deny('commit -n bypasses git hooks.');
      return null;
    case 'filter-repo':
      // git filter-repo refuses to run outside a fresh clone unless forced.
      if (args.includes('--force') || hasShort(args, 'f')) return deny('git filter-repo --force can rewrite a working clone. Run it without --force in a fresh throwaway clone.');
      return null;
    case 'filter-branch':
    case 'replace':
      return deny('history rewrite. Use git filter-repo in a fresh throwaway clone instead.');
    case 'rebase':
      return ask('rebase rewrites commits. Confirm none of them are on Gitea or GitHub yet.');
    case 'reset':
      if (args.includes('--hard')) return ask('reset --hard throws away uncommitted work.');
      return null;
    case 'clean':
      if (args.includes('--force') || hasShort(args, 'f')) return ask('clean -f deletes untracked files.');
      return null;
    case 'sparse-checkout': {
      const action = (args.find((a) => !a.startsWith('-')) ?? '').toLowerCase();
      if (action === 'disable') return deny('sparse-checkout disable would check out hosts/x3/live/systemd (names Windows cannot use).');
      if (args.includes('--no-cone')) return deny('non-cone sparse checkout. Keep cone mode in this clone.');
      if (action === 'set' || action === 'add') {
        if (args.includes('--stdin')) return deny('sparse-checkout --stdin hides the paths from this guard.');
        const paths = args.filter((a) => !a.startsWith('-')).slice(1).map(normPath);
        if (paths.some((p) => SYSTEMD_CONE.includes(p) || p.startsWith('hosts/x3/live/systemd/'))) {
          return deny('that sparse-checkout path would check out hosts/x3/live/systemd (names Windows cannot use).');
        }
      }
      return null;
    }
    default:
      return null;
  }
}

function argObject(envelope) {
  for (const value of [envelope.toolArgs, envelope.tool_input]) {
    if (value === undefined || value === null) continue;
    let args = value;
    if (typeof args === 'string') {
      if (args.trim() === '') continue;
      try {
        args = JSON.parse(args);
      } catch {
        return { unreadable: true };
      }
    }
    if (typeof args !== 'object' || Array.isArray(args)) return { unreadable: true };
    return { args };
  }
  return { args: null };
}

export function classifyShell(command) {
  if (typeof command !== 'string' || command.trim() === '') return deny('shell call with missing or unreadable command text.');
  if (command.length > MAX_COMMAND_CHARS) return deny('shell command too large to inspect.');
  let pending = null;
  for (const tokens of segments(command)) {
    const git = parseGit(tokens);
    if (tokens.some(isSecretPath) && !(git && NAME_ONLY_GIT.has(git.sub))) {
      return deny('touches a secret file (auth.json, mcp.json, models.json, .env, *.token, *.cred, ~/.ssh, /etc/evo-x3). Check secret files by name with git ls-files instead.');
    }
    if (!git) continue;
    const result = classifyGit(git);
    if (result?.permissionDecision === 'deny') return result;
    pending ??= result;
  }
  return pending;
}

export function decide(envelope) {
  const rawName = envelope.toolName ?? envelope.tool_name;
  if (typeof rawName !== 'string') return NO_DECISION;
  const name = rawName.toLowerCase();
  if (!SHELL_TOOLS.has(name) && !PATH_TOOLS.has(name)) return NO_DECISION;

  const { args, unreadable } = argObject(envelope);
  if (unreadable) return deny('tool arguments could not be read.');

  if (SHELL_TOOLS.has(name)) return classifyShell(args?.command) ?? NO_DECISION;

  const paths = PATH_KEYS.flatMap((key) => {
    const value = args?.[key];
    return Array.isArray(value) ? value : [value];
  });
  if (paths.some(isSecretPath)) return deny('reads a secret file. Check secret files by name with git ls-files instead.');
  return NO_DECISION;
}

export function main(raw) {
  const text = typeof raw === 'string' ? raw.replace(/^\uFEFF/, '') : '';
  if (text.trim() === '') return NO_DECISION;
  let envelope;
  try {
    envelope = JSON.parse(text);
  } catch {
    return NO_DECISION;
  }
  if (envelope === null || typeof envelope !== 'object' || Array.isArray(envelope)) return NO_DECISION;
  return decide(envelope);
}

export function runHook(readInput = () => readFileSync(0, 'utf8')) {
  try {
    return main(readInput());
  } catch {
    return deny('internal hook error, so the call is refused. Report it instead of retrying another way.');
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.stdout.write(`${JSON.stringify(runHook())}\n`);
}
