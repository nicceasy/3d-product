#!/usr/bin/env node
// Installs the /3d-product skill into a Claude Code skills folder. No dependencies.
//   npx 3d-product                 install for you (~/.claude/skills/3d-product)
//   npx 3d-product --project       install into this project (./.claude/skills/3d-product)
//   npx 3d-product --dir <path>    install into <path>/3d-product
//   npx 3d-product --force         replace an existing install (the old copy goes to ../skill-backups/)
//   npx 3d-product uninstall       remove it (moved to ../skill-backups/, never deleted)
//   npx 3d-product --dry-run       show what would happen
import { cpSync, existsSync, readFileSync, renameSync, mkdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const NAME = '3d-product';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const src = join(root, 'skills', NAME);
const { version } = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));

const args = process.argv.slice(2);
const has = (f) => args.includes(f);
const val = (f) => { const i = args.indexOf(f); return i >= 0 ? args[i + 1] : undefined; };

if (has('-h') || has('--help')) {
  console.log(`${NAME} ${version}: installs the /${NAME} Claude Code skill.

Usage:
  npx ${NAME} [install] [--project | --dir <path>] [--force] [--dry-run]
  npx ${NAME} uninstall [--project | --dir <path>] [--dry-run]

Targets:
  (default)      ~/.claude/skills/${NAME}   (available in every project)
  --project      ./.claude/skills/${NAME}   (this project only; commit it to share with a team)
  --dir <path>   <path>/${NAME}`);
  process.exit(0);
}
if (has('-v') || has('--version')) { console.log(version); process.exit(0); }

const cmd = args[0] && !args[0].startsWith('-') ? args[0] : 'install';
if (!['install', 'uninstall'].includes(cmd)) { console.error(`Unknown command "${cmd}". Try --help.`); process.exit(1); }
if (has('--dir') && !val('--dir')) { console.error('--dir needs a path.'); process.exit(1); }

const base = val('--dir') ? resolve(val('--dir')) : has('--project') ? resolve('.claude', 'skills') : join(homedir(), '.claude', 'skills');
const dest = join(base, NAME);
const dry = has('--dry-run');
const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\..*/, '').replace('T', '-');
// Backups live beside the skills folder, not in it, so Claude Code never loads an old copy as a second skill.
const backup = join(dirname(base), 'skill-backups', `${NAME}-${stamp}`);

function moveAside() {
  console.log(`${dry ? '[dry run] would move' : 'Moved'} the existing copy to ${backup}`);
  if (!dry) { mkdirSync(dirname(backup), { recursive: true }); renameSync(dest, backup); }
}

if (cmd === 'uninstall') {
  if (!existsSync(dest)) { console.log(`Nothing to remove: ${dest} does not exist.`); process.exit(0); }
  moveAside();
  console.log(`/${NAME} removed from ${base}. Delete the backup folder when you no longer need it.`);
  process.exit(0);
}

if (!existsSync(join(src, 'SKILL.md'))) { console.error(`The package is missing ${src}/SKILL.md.`); process.exit(1); }
if (existsSync(dest)) {
  if (!has('--force')) {
    console.error(`${dest} already exists. Run again with --force to replace it (the old copy is kept as a backup).`);
    process.exit(1);
  }
  moveAside();
}
console.log(`${dry ? '[dry run] would copy' : 'Copying'} /${NAME} ${version} to ${dest}`);
if (!dry) {
  mkdirSync(base, { recursive: true });
  cpSync(src, dest, { recursive: true, filter: (p) => !p.includes('__pycache__') && !p.endsWith('.DS_Store') });
}
console.log(`Done. Restart Claude Code (or start a new session), then ask for a product film or type /${NAME}.`);
