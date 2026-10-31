// Turns one recording from record-demo.mjs into the README assets (method adapted
// from Reflect).
//
//   node make-assets.mjs [output/<timestamp>]     (default: the newest recording)
//
// Needs ffmpeg and ffprobe on PATH. A live recording writes to docs/assets/; a mock
// rehearsal writes to <run>/assets/ only, so fake answers never reach the README.
//
// Playwright's video does not keep real time (headless Chromium sends a frame only
// on repaint), so every mark is placed in VIDEO time by reading the phase number the
// recorder painted, in binary, into five black/white cells in the bottom-right corner.
//
// The edit CUTS, never speeds up:
//   - each planned hold is exactly HOLD seconds (one frame from its midpoint, held);
//   - each server wait (wait:<x> .. wait-end:<x>) keeps its first WAIT_KEEP seconds,
//     so the spinner or typing dots are seen, and the rest is cut;
//   - every other still stretch (freezedetect) keeps WAIT_KEEP seconds.
// Then it checks its own output (holds exactly HOLD, nothing else still for longer),
// writes 1 fps contact sheets for a person to look at, and exits non-zero on failure.

import { copyFileSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { execFileSync, spawnSync } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const runs = readdirSync(join(HERE, 'output')).filter((d) => /^\d{4}-/.test(d)).sort();
const RUN = resolve(HERE, process.argv[2] ?? join('output', runs.at(-1)));
const { video, timeline, mock } = JSON.parse(readFileSync(join(RUN, 'timeline.json'), 'utf8'));
const ASSETS = mock ? join(RUN, 'assets') : resolve(HERE, '..', '..', 'docs', 'assets');
const ffmpeg = (...args) => execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...args], { stdio: 'inherit' });
const probe = (file) => +spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of',
  'default=nw=1:nk=1', file], { encoding: 'utf8' }).stdout.trim();

const HOLD = 2.5;
const WAIT_KEEP = 1.0;
// -78 dB, not Reflect's -60: here the injected cursor is often the only thing moving, and
// an 18 px dot changes so few pixels that -60 dB called its glides 'still' and cut them.
const FREEZE = 'freezedetect=n=-78dB:d=0.9';
// The raw pass also looks for short stills (0.2 s), so the settled moment just before a
// hold, which shows the same picture as the hold, is cut whole instead of lengthening it.
const RAW_FREEZE = 'freezedetect=n=-78dB:d=0.2';
// The marker is 50×10 CSS px; the page is drawn at (video width / 1280)×, so 75×15 at 1080p.
const width = +spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width',
  '-of', 'default=nw=1:nk=1', video], { encoding: 'utf8' }).stdout.trim();
const S = width / 1280;
const [MW, MH] = [Math.round(50 * S), Math.round(10 * S)];
const MARKER = `crop=${MW - 2}:${MH - 2}:iw-${MW - 1}:ih-${MH - 1},scale=5:1:flags=area,format=gray`;
const COVER = `drawbox=x=iw-${MW}:y=ih-${MH}:w=${MW}:h=${MH}:color=0x08060E@1:t=fill`;

// Holds are measured at -60 dB: a held frame is one frame repeated, but the encoder keeps
// refining it for a few frames, which -78 dB would count as movement.
const HOLD_FREEZE = 'freezedetect=n=-60dB:d=0.9';

function freezes(file, filter = FREEZE) {
  const err = spawnSync('ffmpeg', ['-hide_banner', '-i', file, '-vf', filter, '-map', '0:v', '-f', 'null', '-'],
    { encoding: 'utf8' }).stderr;
  const starts = [...err.matchAll(/freeze_start: ([\d.]+)/g)].map((m) => +m[1]);
  const ends = [...err.matchAll(/freeze_end: ([\d.]+)/g)].map((m) => +m[1]);
  return starts.map((s, i) => ({ start: s, end: ends[i] ?? probe(file) }));
}

// 1. Read the phase marker: the video time at which each phase first appears.
const read = spawnSync('ffmpeg', ['-hide_banner', '-i', video, '-vf', `${MARKER},showinfo`,
  '-f', 'rawvideo', '-'], { maxBuffer: 1 << 28 });
const pts = [...read.stderr.toString().matchAll(/pts_time:([\d.]+)/g)].map((m) => +m[1]);
const firstSeen = new Map();
for (let f = 0; f < pts.length && (f + 1) * 5 <= read.stdout.length; f++) {
  let phase = 0;
  for (let i = 0; i < 5; i++) if (read.stdout[f * 5 + i] > 128) phase |= 1 << i;
  if (phase > 0 && !firstSeen.has(phase)) firstSeen.set(phase, pts[f]);
}
const at = (event) => {
  const e = timeline.find((x) => x.event === event);
  if (!e) throw new Error(`no mark ${event}`);
  for (let p = e.phase; p <= e.phase + 3; p++) if (firstSeen.has(p)) return firstSeen.get(p);
  throw new Error(`phase ${e.phase} (${event}) not found in the video`);
};

const videoEnd = probe(video);
const start = at('start');
const end = Math.min(at('end') + 0.04, videoEnd); // the last hold is the last picture
const holds = timeline.filter((e) => e.event.startsWith('hold:')).map((e) => {
  const name = e.event.slice(5);
  return { name, start: at(`hold:${name}`), end: at(`hold-end:${name}`) };
});

// 2. Cuts: server waits, then still stretches outside the holds.
const cuts = [];
for (const e of timeline.filter((x) => x.event.startsWith('wait:'))) {
  const name = e.event.slice(5);
  const a = at(`wait:${name}`) + WAIT_KEEP;
  const b = at(`wait-end:${name}`) - 0.2;
  if (b - a > 0.3) cuts.push({ from: a, to: b, kind: `wait ${name}`, still: +(b - a + WAIT_KEEP).toFixed(2) });
}
const outsideHolds = (a, b) => {
  let pieces = [[a, b]];
  for (const h of holds) {
    pieces = pieces.flatMap(([x, y]) => (y <= h.start || x >= h.end ? [[x, y]]
      : [[x, Math.min(y, h.start)], [Math.max(x, h.end), y]].filter(([p, q]) => q - p > 0.05)));
  }
  return pieces;
};
const touchesHold = (a, b) => holds.some((h) => Math.abs(b - h.start) < 0.1 || Math.abs(a - h.end) < 0.1);
for (const f of freezes(video, RAW_FREEZE)) {
  if (f.end <= start || f.start >= end) continue;
  for (const [a, b] of outsideHolds(Math.max(f.start, start), Math.min(f.end, end))) {
    const keep = touchesHold(a, b) ? 0 : WAIT_KEEP;
    if (b - a > keep + 0.05) cuts.push({ from: a + keep, to: b, kind: keep ? 'still' : 'beside hold', still: +(b - a).toFixed(2) });
  }
}
cuts.sort((a, b) => a.from - b.from);
for (let i = 1; i < cuts.length; i++) {
  if (cuts[i].from <= cuts[i - 1].to) { cuts[i - 1].to = Math.max(cuts[i - 1].to, cuts[i].to); cuts.splice(i--, 1); }
}

// 3. Segments that survive the cuts, each hold rebuilt to exactly HOLD.
const keep = [];
let pos = start;
for (const c of cuts) { if (c.from > pos) keep.push([pos, c.from]); pos = Math.max(pos, c.to); }
if (end > pos) keep.push([pos, end]);
const segments = [];
for (const [a, b] of keep) {
  let x = a;
  for (const h of holds.filter((h) => h.start < b && h.end > a)) {
    if (h.start > x) segments.push({ a: x, b: h.start, pad: 0 });
    const mid = h.start + (h.end - h.start) / 2;
    segments.push({ a: mid, b: mid + 0.04, pad: HOLD - 0.04, hold: h.name });
    x = h.end;
  }
  if (b > x) segments.push({ a: x, b, pad: 0 });
}
const remap = (t) => {
  let out = 0;
  for (const s of segments) {
    if (t >= s.b) out += s.b - s.a + s.pad;
    else if (t > s.a) return out + (t - s.a);
    else return out;
  }
  return out;
};

mkdirSync(ASSETS, { recursive: true });
const mp4 = join(ASSETS, 'visionaryx-demo.mp4');
const parts = segments.map((s, i) => (s.hold
  ? `[0:v]trim=start=${s.a},setpts=PTS-STARTPTS,trim=end_frame=1,setpts=N/25/TB,fps=25,tpad=stop_mode=clone:stop_duration=${s.pad}[v${i}]`
  : `[0:v]trim=start=${s.a}:end=${s.b},setpts=PTS-STARTPTS[v${i}]`));
const filter = `${parts.join(';')};${segments.map((_, i) => `[v${i}]`).join('')}`
  + `concat=n=${segments.length}:v=1:a=0,${COVER}[out]`;
ffmpeg('-i', video, '-filter_complex', filter, '-map', '[out]', '-c:v', 'libx264', '-preset', 'slow',
  '-crf', '24', '-pix_fmt', 'yuv420p', '-r', '25', '-movflags', '+faststart', mp4);

// 4. GIF: PDF Chat, the 14 s that end on the held, cited answer (the question typed,
// the answer and its sources arriving).
const gEnd = remap(at('hold-end:pdf-answer'));
const gStart = Math.max(remap(at('pdf')) - 0.3, gEnd - 14);
const gDur = gEnd - gStart;
const palette = join(RUN, 'palette.png');
const gifFilters = 'fps=12,scale=1280:-1:flags=lanczos';
ffmpeg('-ss', `${gStart}`, '-t', `${gDur}`, '-i', mp4, '-vf', `${gifFilters},palettegen=stats_mode=diff`, palette);
ffmpeg('-ss', `${gStart}`, '-t', `${gDur}`, '-i', mp4, '-i', palette,
  '-lavfi', `${gifFilters} [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle`,
  join(ASSETS, 'visionaryx-demo.gif'));

// 5. Screenshots (taken settled, cursor and marker hidden).
for (const [from, to] of [
  ['01-landing.png', 'landing.png'],
  ['02-pdf-answer.png', 'pdf-answer.png'],
  ['03-image-query.png', 'image-query.png'],
  ['04-text-to-image.png', 'text-to-image.png'],
]) copyFileSync(join(RUN, from), join(ASSETS, to));

// 6. Self-check.
const finalSeconds = probe(mp4);
const finalStill = freezes(mp4);
const holdStill = freezes(mp4, HOLD_FREEZE);
const holdChecks = holds.map((h) => {
  // The still stretch that overlaps the rebuilt hold the most (a neighbouring stretch can
  // end a few frames into the hold and must not be mistaken for it).
  const a = remap(h.start), b = a + HOLD;
  const overlap = (s) => Math.min(s.end, b) - Math.max(s.start, a);
  const f = holdStill.filter((s) => overlap(s) > 0).sort((x, y) => overlap(y) - overlap(x))[0];
  return { name: h.name, seconds: f ? +(f.end - f.start).toFixed(2) : 0 };
});
const badHolds = holdChecks.filter((h) => h.seconds < HOLD - 0.2);
const tooLong = finalStill.filter((s) => s.end - s.start > HOLD + 0.3)
  .map((s) => ({ start: +s.start.toFixed(2), seconds: +(s.end - s.start).toFixed(2) }));
ffmpeg('-i', mp4, '-vf', 'fps=1,scale=384:-1,tile=5x4', join(RUN, 'contact-%02d.png'));

writeFileSync(join(RUN, 'edit.json'), JSON.stringify({
  final_seconds: finalSeconds, video_seconds: videoEnd,
  phases_seen: Object.fromEntries(firstSeen), holds: holdChecks, cuts, segments,
  still_longer_than_a_hold: tooLong, gif: { start: +gStart.toFixed(2), seconds: +gDur.toFixed(2) },
  marks_in_final: Object.fromEntries(timeline.map((e) => [e.event, +remap(at(e.event)).toFixed(2)])),
}, null, 2));
for (const f of readdirSync(ASSETS)) console.log(`${f.padEnd(24)} ${(statSync(join(ASSETS, f)).size / 1024 / 1024).toFixed(2)} MB`);
console.log(`assets: ${ASSETS}`);
console.log(`final ${finalSeconds.toFixed(1)} s (raw video ${videoEnd.toFixed(1)} s); ${cuts.length} cuts; holds ${holdChecks.map((h) => `${h.name} ${h.seconds}s`).join(', ')}`);
console.log(`still for longer than a hold: ${tooLong.length ? JSON.stringify(tooLong) : 'none'}`);
console.log(`contact sheets: ${join(RUN, 'contact-*.png')} (tile n of sheet k = second 20(k-1)+n)`);
if (badHolds.length || tooLong.length) {
  console.error(`CHECK FAILED: short holds ${JSON.stringify(badHolds)}, long stills ${JSON.stringify(tooLong)}`);
  process.exitCode = 1;
}
