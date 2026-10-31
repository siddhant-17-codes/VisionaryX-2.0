// Records the README demo by driving VisionaryX in Chromium (method adapted from Reflect).
//
//   node record-demo.mjs                 live site, real models (costs quota, see README)
//   DEMO_MOCK=1 node record-demo.mjs     rehearsal: VX_BASE_URL is a local dev server and
//                                        every API call is answered by a fake, at no cost
//
// Writes to scripts/demo/output/<timestamp>/ (gitignored): the raw .webm, screenshots
// and timeline.json, which make-assets.mjs turns into the final video.
//
// Nothing goes on camera half-drawn: before each step the recorder waits for network
// idle, webfonts and every finite CSS animation. Headless Chromium draws no pointer,
// so an injected dot moves along eased paths and pulses on clicks.
//
// Every server round trip is bracketed by `wait:<name>` / `wait-end:<name>` marks, so
// the editor can cut the waiting (cold indexing, model calls) instead of speeding it up.
//
// Secret guard: every API response and the final page text are searched for the key
// and token values in backend/.env (never printed). A live run also deletes the
// conversations it created, through the API, after the video stops.

import { chromium } from 'playwright';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, '..', '..');
const MOCK = !!process.env.DEMO_MOCK;
const BASE_URL = process.env.VX_BASE_URL ?? (MOCK ? 'http://localhost:5199' : 'https://visionaryx-dusky.vercel.app');
const API_URL = process.env.VX_API_URL ?? (MOCK ? 'http://localhost:8999' : 'https://visionaryx-backend.onrender.com');
const EX = (f) => join(REPO, 'examples', f);
const DOCS = [EX('lumen_ridge_annual_report_2025.pdf'), EX('lumen_ridge_cold_storage_plan.docx')];
const CHART = EX('lumen_ridge_harvest_chart.png');
const PDF_QUESTION = 'When will the new cold-storage building open, and what will it cost?';
const CHAT_MESSAGE = 'Explain retrieval-augmented generation in three short numbered steps.';
const IMAGE_QUESTION = 'Which year had the biggest harvest, and how much did it grow on the year before?';
const IMAGE_PROMPT = 'A watercolour of an apple orchard at sunrise, with a small wooden cold-storage barn';
// The app's text is small, so the page is laid out at 1280×720 CSS px and drawn at 1.5×:
// the video and screenshots are 1920×1080 with text that stays readable. The scale is
// forced on the browser itself (a 1280×720 window at 1.5×): Playwright's emulated
// deviceScaleFactor does not reach its video, which would come out 1280×720.
const VIEWPORT = { width: 1280, height: 720 };
const SCALE = 1.5;
const FRAME = { width: VIEWPORT.width * SCALE, height: VIEWPORT.height * SCALE };
const HOLD_MS = 2500; // the only deliberate pauses: the PDF answer, the image answer, the generated image

const stamp = new Date().toISOString().replace(/[:.]/g, '-');
const OUT = join(HERE, 'output', stamp);
mkdirSync(OUT, { recursive: true });

const secrets = loadSecrets(join(REPO, 'backend', '.env'));
const secretHits = [];
const timeline = [];
const holds = [];
let t0 = 0;
const now = () => +((Date.now() - t0) / 1000).toFixed(2);
let phaseNo = 0;
const pause = (ms) => new Promise((r) => setTimeout(r, ms));

// Advance the on-screen phase marker (five black/white cells = the phase in binary),
// wait two frames so it is painted, then record the event against that phase.
async function mark(page, event) {
  phaseNo += 1;
  await page.evaluate((n) => {
    const cells = document.getElementById('__demo_phase')?.children ?? [];
    for (let i = 0; i < cells.length; i++) cells[i].style.background = (n >> i) & 1 ? '#fff' : '#000';
    return new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  }, phaseNo);
  timeline.push({ event, phase: phaseNo, seconds: now() });
}

function loadSecrets(envFile) {
  if (!existsSync(envFile)) return [];
  return readFileSync(envFile, 'utf8').split(/\r?\n/)
    .map((l) => l.match(/^\s*([A-Z_]*(?:KEY|TOKEN)[A-Z_]*)\s*=\s*(.+?)\s*$/))
    .filter(Boolean).map((m) => m[2]).filter((v) => v.length >= 12);
}

function checkForSecrets(where, text) {
  if (!text) return;
  if (secrets.some((s) => text.includes(s) || text.includes(s.slice(0, 16)))) secretHits.push(where);
}

// ── Settling ────────────────────────────────────────────────────────────────

async function settled(page) {
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.evaluate(async () => {
    await document.fonts.ready;
    const finite = document.getAnimations().filter((a) => {
      const t = a.effect?.getComputedTiming?.();
      return t && Number.isFinite(t.endTime);
    });
    await Promise.race([
      Promise.all(finite.map((a) => a.finished.catch(() => {}))),
      new Promise((r) => setTimeout(r, 4000)),
    ]);
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  });
}

// ── The cursor ──────────────────────────────────────────────────────────────

const cursor = { x: VIEWPORT.width * 0.62, y: VIEWPORT.height * 0.7 };

async function ensureCursor(page) {
  await page.evaluate(({ x, y }) => {
    if (document.getElementById('__demo_cursor')) return;
    const style = document.createElement('style');
    style.textContent = `
      #__demo_cursor { position: fixed; left: 0; top: 0; width: 18px; height: 18px;
        margin: -9px 0 0 -9px; border-radius: 50%; pointer-events: none;
        z-index: 2147483647; background: rgba(252, 245, 239, 0.92);
        box-shadow: 0 0 0 2px rgba(8, 6, 14, 0.6), 0 2px 8px rgba(0, 0, 0, 0.4); }
      #__demo_cursor.hidden { display: none; }
      .__demo_pulse { position: fixed; width: 18px; height: 18px; margin: -9px 0 0 -9px;
        border-radius: 50%; pointer-events: none; z-index: 2147483646;
        border: 2px solid rgba(252, 245, 239, 0.9); animation: __demo_pulse 520ms ease-out forwards; }
      @keyframes __demo_pulse { from { transform: scale(1); opacity: 0.9; } to { transform: scale(3.2); opacity: 0; } }`;
    document.head.appendChild(style);
    const phase = document.createElement('div');
    phase.id = '__demo_phase';
    phase.style.cssText = 'position:fixed;right:0;bottom:0;width:50px;height:10px;display:flex;pointer-events:none;z-index:2147483647';
    for (let i = 0; i < 5; i++) {
      const cell = document.createElement('div');
      cell.style.cssText = 'width:10px;height:10px;background:#000';
      phase.appendChild(cell);
    }
    document.body.appendChild(phase);
    const dot = document.createElement('div');
    dot.id = '__demo_cursor';
    dot.style.transform = `translate(${x}px, ${y}px)`;
    document.body.appendChild(dot);
    window.addEventListener('mousemove', (e) => { dot.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`; }, true);
    window.addEventListener('mousedown', (e) => {
      const ring = document.createElement('div');
      ring.className = '__demo_pulse';
      ring.style.left = `${e.clientX}px`;
      ring.style.top = `${e.clientY}px`;
      document.body.appendChild(ring);
      setTimeout(() => ring.remove(), 600);
    }, true);
  }, cursor);
}

const setCursorHidden = (page, hidden) => page.evaluate((h) => {
  document.getElementById('__demo_cursor')?.classList.toggle('hidden', h);
  const marker = document.getElementById('__demo_phase');
  if (marker) marker.style.visibility = h ? 'hidden' : 'visible';
}, hidden);

async function glide(page, x, y, ms = 700) {
  await ensureCursor(page);
  const from = { ...cursor };
  const steps = Math.max(8, Math.round(ms / 16));
  for (let i = 1; i <= steps; i++) {
    const p = i / steps;
    const e = p < 0.5 ? 4 * p ** 3 : 1 - (-2 * p + 2) ** 3 / 2;
    cursor.x = from.x + (x - from.x) * e;
    cursor.y = from.y + (y - from.y) * e;
    await page.mouse.move(cursor.x, cursor.y);
    await pause(16);
  }
}

async function glideTo(page, locator, ms = 700) {
  await locator.scrollIntoViewIfNeeded();
  const box = await locator.boundingBox();
  await glide(page, box.x + box.width / 2, box.y + box.height / 2, ms);
}

async function clickAt(page, locator, ms = 700) {
  await glideTo(page, locator, ms);
  await pause(180);
  await page.mouse.down();
  await pause(90);
  await page.mouse.up();
}

async function typeNaturally(page, text) {
  for (const ch of text) {
    await page.keyboard.type(ch);
    await pause(28 + Math.random() * 40 + (ch === ' ' ? 30 : 0));
  }
}

// Smoothly bring an element to the middle of the screen (the workspace scrolls its
// content area, not the window, so this uses the element's own scrollIntoView).
async function bringIntoView(page, locator) {
  await locator.evaluate((el) => el.scrollIntoView({ behavior: 'smooth', block: 'center' }));
  await pause(900);
}

// The settled moments before a hold (screenshot, layout checks) show the same picture as
// the hold, so a short drift of the cursor separates them: the hold alone is the pause.
async function hold(page, name) {
  await glide(page, cursor.x - 70, cursor.y + 40, 700);
  await mark(page, `hold:${name}`);
  const start = now();
  await pause(HOLD_MS);
  await mark(page, `hold-end:${name}`);
  holds.push({ name, start, end: now() });
}

async function shot(page, name) {
  await setCursorHidden(page, true);
  await page.screenshot({ path: join(OUT, name) });
  await setCursorHidden(page, false);
}

async function upload(page, zone, files) {
  const chooser = page.waitForEvent('filechooser');
  await clickAt(page, zone, 900);
  await (await chooser).setFiles(files);
}

// ── Rehearsal fakes (DEMO_MOCK=1 only) ──────────────────────────────────────

async function installMocks(page) {
  const chart = readFileSync(CHART).toString('base64');
  const sessions = [];
  const reply = (route, body, status = 200) => route.fulfill({
    status, contentType: 'application/json', body: JSON.stringify(body),
    headers: { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*' },
  });
  await page.route(`${API_URL}/**`, async (route) => {
    const req = route.request();
    const path = new URL(req.url()).pathname;
    if (req.method() === 'OPTIONS') return reply(route, {});
    if (path === '/health') return reply(route, { status: 'ok' });
    if (path === '/api/generate/status') return reply(route, { available: true, resumes_at: null });
    if (path === '/api/sessions' && req.method() === 'GET') return reply(route, sessions);
    if (path === '/api/sessions' && req.method() === 'POST') {
      const s = { id: `mock-${sessions.length}`, title: 'New chat', mode: JSON.parse(req.postData()).mode,
        created_at: 'x', updated_at: 'x', messages: [], documents: [] };
      sessions.push(s);
      return reply(route, s);
    }
    if (path.startsWith('/api/sessions/')) return reply(route, { detail: 'not found' }, 404);
    await pause(path === '/api/pdf/upload' ? 4000 : 2500);
    if (path === '/api/pdf/upload') return reply(route, { session_id: 'idx', files_processed: 2, questions: [
      'What was the total apple harvest in 2025?', 'When does the cold store open?', 'Who is the treasurer?'] });
    if (path === '/api/pdf/query') return reply(route, {
      answer: 'The new cold-storage building is due to open on **1 September 2026**, in time for the 2026 harvest. The board approved a budget of **600,000 credits**: 410,000 for the building, 150,000 for the cooling system and 40,000 contingency.',
      citations: [
        { source: 'lumen_ridge_cold_storage_plan.docx', page: 0, section: 'Schedule', chunk: 'Groundworks start in March 2026. The building is due to open on 1 September 2026...' },
        { source: 'lumen_ridge_annual_report_2025.pdf', page: 4, section: null, chunk: 'The board approved a new cold-storage building costing 600,000 credits...' },
      ] });
    if (path === '/api/chat') return reply(route, { reply: '1. **Retrieve**: find the passages most relevant to the question.\n2. **Augment**: add them to the prompt as context.\n3. **Generate**: the model answers from that context, citing it.' });
    if (path === '/api/image/query') return reply(route, { answer: '**2025** had the biggest harvest, at **1,870 tonnes**, up **200 tonnes** (about 12%) on 2024.' });
    if (path === '/api/generate/image') return reply(route, { image_base64: chart });
    return reply(route, { detail: 'unmocked' }, 404);
  });
}

// ── The run ─────────────────────────────────────────────────────────────────

async function main() {
  if (!MOCK) {
    // Wake the free backend first, so the recording never shows a cold start.
    for (let i = 0; i < 30; i++) {
      const ok = await fetch(`${API_URL}/health`).then((r) => r.ok).catch(() => false);
      if (ok) break;
      await pause(5000);
    }
  }
  const browser = await chromium.launch({
    args: [`--force-device-scale-factor=${SCALE}`, `--window-size=${VIEWPORT.width},${VIEWPORT.height}`] });
  const context = await browser.newContext({ viewport: null, recordVideo: { dir: OUT, size: FRAME } });
  t0 = Date.now();
  const page = await context.newPage();
  if (MOCK) await installMocks(page);

  const responseChecks = [];
  page.on('response', (res) => {
    if (!res.url().startsWith(API_URL)) return;
    responseChecks.push(res.text().then((b) => checkForSecrets(new URL(res.url()).pathname, b)).catch(() => {}));
  });
  const consoleErrors = [];
  page.on('console', (m) => m.type() === 'error' && consoleErrors.push(m.text()));

  // 1. Landing: the hero, then straight to PDF Chat through its feature card.
  await page.goto(BASE_URL, { waitUntil: 'load' });
  await settled(page);
  await ensureCursor(page);
  await mark(page, 'start');
  await shot(page, '01-landing.png');
  const clientId = await page.evaluate(() => localStorage.getItem('vx_client_id'));
  await glide(page, VIEWPORT.width * 0.5, VIEWPORT.height * 0.62, 900);
  await clickAt(page, page.getByRole('link', { name: /PDF Chat \+ RAG/ }), 1000);

  // 2. PDF Chat: two documents at once, one question across both.
  await page.waitForURL('**/workspace/pdf');
  await settled(page);
  await mark(page, 'pdf');
  await upload(page, page.getByRole('button', { name: 'Upload PDF or DOCX files' }), DOCS);
  await mark(page, 'wait:upload');
  await page.getByText('RAG active').waitFor({ timeout: 150_000 });
  await mark(page, 'wait-end:upload');
  await settled(page);
  const box = page.getByPlaceholder('Ask about your document…');
  await clickAt(page, box, 900);
  await typeNaturally(page, PDF_QUESTION);
  await clickAt(page, page.getByRole('button', { name: 'Send message' }), 500);
  await mark(page, 'wait:pdf-answer');
  await page.getByText('Sources', { exact: true }).waitFor({ timeout: 120_000 });
  await page.waitForFunction(() => !document.querySelector('textarea')?.disabled, null, { timeout: 30_000 });
  await mark(page, 'wait-end:pdf-answer');
  await glide(page, VIEWPORT.width * 0.85, VIEWPORT.height * 0.45, 700);
  await settled(page);
  await shot(page, '02-pdf-answer.png');
  await hold(page, 'pdf-answer');

  // 3. General chat: one message, an answer with a numbered list.
  await clickAt(page, page.getByRole('link', { name: 'Chat', exact: true }), 900);
  await page.waitForURL('**/workspace/chat');
  await settled(page);
  await mark(page, 'chat');
  await clickAt(page, page.getByPlaceholder('Ask VisionaryX anything…'), 800);
  await typeNaturally(page, CHAT_MESSAGE);
  await page.keyboard.press('Enter');
  await mark(page, 'wait:chat');
  // The input is disabled from send until the answer has fully revealed.
  await page.waitForFunction(() => document.querySelector('textarea')?.disabled, null, { timeout: 10_000 }).catch(() => {});
  await page.waitForFunction(() => !document.querySelector('textarea')?.disabled, null, { timeout: 120_000 });
  await mark(page, 'wait-end:chat');
  await pause(1100); // the reveal (at most 1 s) plays out on camera
  await mark(page, 'chat-read');
  // Read the answer: a slow sweep down its numbered list, so the frame never sits still.
  const answer = await page.locator('ol').last().boundingBox();
  if (answer) {
    await glide(page, answer.x + 40, answer.y + 8, 600);
    await glide(page, answer.x + Math.min(answer.width, 520), answer.y + answer.height - 6, 2200);
  }

  // 4. Image Query: a chart, one question.
  await clickAt(page, page.getByRole('link', { name: 'Image Query' }), 900);
  await page.waitForURL('**/workspace/image');
  await settled(page);
  await mark(page, 'image');
  await upload(page, page.getByRole('button', { name: 'Upload an image' }), CHART);
  await settled(page);
  await clickAt(page, page.getByPlaceholder('Ask a specific question about the image (optional)'), 800);
  await typeNaturally(page, IMAGE_QUESTION);
  await clickAt(page, page.getByRole('button', { name: 'Analyse Image' }), 600);
  await mark(page, 'wait:image-answer');
  await page.getByText('VisionaryX Response').waitFor({ timeout: 120_000 });
  await page.getByRole('button', { name: 'Analyse Image' }).waitFor({ timeout: 60_000 });
  await mark(page, 'wait-end:image-answer');
  await bringIntoView(page, page.getByText('VisionaryX Response'));
  await pause(400);
  await settled(page);
  await shot(page, '03-image-query.png');
  await hold(page, 'image-answer');

  // 5. Text to Image: one prompt, one image.
  await clickAt(page, page.getByRole('link', { name: 'Text to Image' }), 900);
  await page.waitForURL('**/workspace/generate');
  await settled(page);
  await mark(page, 'generate');
  await clickAt(page, page.locator('textarea'), 800);
  await typeNaturally(page, IMAGE_PROMPT);
  await clickAt(page, page.getByRole('button', { name: 'Generate Image' }), 600);
  await mark(page, 'wait:generated');
  await page.getByAltText('generated').waitFor({ timeout: 150_000 });
  await mark(page, 'wait-end:generated');
  await bringIntoView(page, page.getByAltText('generated'));
  await settled(page);
  await shot(page, '04-text-to-image.png');
  await hold(page, 'generated');
  await mark(page, 'end');
  await pause(1000);

  checkForSecrets('page text', await page.locator('body').innerText());
  await Promise.all(responseChecks);
  const video = page.video();
  await context.close();
  await browser.close();

  // A live run removes everything it created (only this browser's own sessions).
  let cleanup = 'skipped (mock)';
  if (!MOCK && clientId) {
    const h = { 'X-Client-Id': clientId };
    const mine = await fetch(`${API_URL}/api/sessions`, { headers: h }).then((r) => r.json());
    for (const s of mine) await fetch(`${API_URL}/api/sessions/${s.id}`, { method: 'DELETE', headers: h });
    const left = await fetch(`${API_URL}/api/sessions`, { headers: h }).then((r) => r.json());
    cleanup = `deleted ${mine.length} session(s); ${left.length} left`;
  }

  writeFileSync(join(OUT, 'timeline.json'),
    JSON.stringify({ video: await video.path(), timeline, holds, consoleErrors, mock: MOCK }, null, 2));
  console.log(`output: ${OUT}`);
  console.log(`raw ≈ ${now().toFixed(1)}s; holds: ${holds.map((x) => `${x.name} ${(x.end - x.start).toFixed(1)}s`).join(', ')}; console errors: ${consoleErrors.length}`);
  console.log(`cleanup: ${cleanup}`);
  console.log(`secret guard: ${secretHits.length ? 'FOUND in ' + secretHits.join(', ') : `none of ${secrets.length} key/token values found in any API response or page text`}`);
  if (secretHits.length) process.exit(2);
}

main().catch((err) => {
  console.error('demo recording failed:', err.message);
  process.exit(1);
});
