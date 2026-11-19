// gta6-meme-x-01 entrypoint (Node 22, standard library only).
//
// The entry is the X post itself: the meme (meme.png, built in-session by
// generate-meme.py) is posted on X from a public account, and POST.json at
// this repository's root names the post. All this program does is copy
// POST.json from the repository into /output, where the house gate reads it
// and then reads the post from X. Nothing the program writes is judged.
//
// Run locally the way the grader does, with the two stand-ins:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const source = join(BOT_DIR, 'POST.json');

if (!existsSync(source)) {
  console.error(`POST.json not found in ${BOT_DIR}`);
  process.exit(1);
}

// Refuse to copy a post file that is not even shaped like one: the gate
// needs a JSON object with a url string, and a broken file should fail
// loudly here instead of silently passing through.
const parsed: unknown = JSON.parse(readFileSync(source, 'utf8'));
if (
  typeof parsed !== 'object' ||
  parsed === null ||
  Array.isArray(parsed) ||
  typeof (parsed as { url?: unknown }).url !== 'string'
) {
  console.error('POST.json must be a JSON object with a string "url" field');
  process.exit(1);
}

const url = (parsed as { url: string }).url;

// A real post address is https://x.com/<handle>/status/<digits> (or the
// twitter.com / /i/web/status/ forms). The kit placeholder still passes
// through untouched so the file can be checked before the post exists;
// the gate refuses the placeholder itself.
if (!url.includes('<handle>') && !url.includes('<id>')) {
  const ok = /^https:\/\/(www\.|mobile\.)?(x\.com|twitter\.com)\/[^/]+\/status\/\d+$/.test(
    url,
  ) || /^https:\/\/(www\.|mobile\.)?(x\.com|twitter\.com)\/i\/web\/status\/\d+$/.test(url);
  if (!ok) {
    console.error(`POST.json url is not an X post address: ${url}`);
    process.exit(1);
  }
}

mkdirSync(OUTPUT_DIR, { recursive: true });
copyFileSync(source, join(OUTPUT_DIR, 'POST.json'));
console.log(`copied POST.json -> ${join(OUTPUT_DIR, 'POST.json')}`);
