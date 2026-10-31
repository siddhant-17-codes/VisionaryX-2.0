# `scripts/demo/`: recording the README demo

Drives the real VisionaryX app in Chromium with Playwright: PDF Chat with both files in
[`examples/`](../../examples/), General Chat, Image Query and Text to Image, in one take.
Not product code, and kept out of the frontend's dependencies on purpose. The method is
the one used for the author's Reflect project.

## Run it

Needs Node.js, and `ffmpeg` and `ffprobe` on `PATH`.

```bash
cd scripts/demo
npm ci
npx playwright install chromium
node record-demo.mjs          # live site, real models (see "Cost")
node make-assets.mjs          # cut the newest recording into docs/assets/
```

**Rehearse first, at no cost.** Build the frontend against a fake API address and serve
it on port 5199; with `DEMO_MOCK=1` the recorder answers every API call itself:

```bash
cd frontend
VITE_API_URL=http://localhost:8999 npx vite build --outDir ../scripts/demo/output/mockdist
npx vite preview --outDir ../scripts/demo/output/mockdist --port 5199
# second terminal
cd scripts/demo
DEMO_MOCK=1 node record-demo.mjs && node make-assets.mjs
```

A rehearsal writes its assets to `output/<run>/assets/` only, so fake answers never reach
the README. `VX_BASE_URL` and `VX_API_URL` point the recorder at other deployments.

## What the recorder does (`record-demo.mjs`)

- **1920×1080 with readable text.** The page is laid out at 1280×720 CSS pixels and drawn
  at 1.5×. The scale is forced on the browser itself (`--force-device-scale-factor`):
  Playwright's emulated `deviceScaleFactor` does not reach its video, which then comes out
  1280×720 padded with grey.
- **Nothing goes on camera half-drawn.** Before each step it waits for network idle,
  `document.fonts.ready` and every finite CSS animation (`document.getAnimations()`).
- **A visible cursor.** Headless Chromium draws none, so an injected dot moves along
  eased paths and pulses on each click; it is hidden for screenshots. Uploads are real
  clicks on the drop zones, answered through Playwright's file chooser. Text is typed
  with per-key jitter.
- **Three deliberate holds** of 2.5 s: the cited PDF answer, the image answer and the
  generated image. A short cursor drift just before each hold keeps the settled moment
  before it from merging into the pause.
- **A timeline written into the video itself.** Playwright's video does not keep real
  time (headless Chromium sends a frame only when the page repaints), so wall-clock
  timestamps cannot place a cut. At every mark the recorder sets a 50×10 px strip in the
  bottom-right corner to the phase number in binary (five black-or-white cells);
  `timeline.json` records which phase each event is. Every server round trip is bracketed
  by `wait:` / `wait-end:` marks.
- **Clean-up.** A live run deletes every conversation it created, through the API, with
  the browser's own `X-Client-Id`, and prints how many are left (should be 0).
- **Secret guard.** Every API response body and the final page text are searched for the
  key and token values in `backend/.env`. It prints only whether one was found, never a
  value, and exits non-zero if one was.

## What the editor does (`make-assets.mjs`)

It reads the phase strip frame by frame, so every mark is placed in **video** time, then
paints the strip over. It **cuts, never speeds up**:

- Each hold is exactly 2.5 s: one frame from the hold's midpoint, held.
- Each server wait keeps its first second (the spinner or typing dots are seen), and the
  rest is cut.
- `ffmpeg freezedetect` finds every other still stretch; each keeps at most a second,
  except stillness running straight into or out of a hold, which is cut whole.

It then checks its own output and **exits non-zero** if a hold is short or anything else
stays still for longer than a hold, and writes one-frame-per-second contact sheets
(`contact-NN.png`, 20 tiles each, tile *n* of sheet *k* = second 20(*k*−1)+*n*) for a
person to look at before the assets are used. Every cut and hold is in `edit.json`.

Outputs in `docs/assets/`: four 1920×1080 screenshots, `visionaryx-demo.gif` (the 14 s of
PDF Chat that end on the cited answer, 1280 px wide) and `visionaryx-demo.mp4`
(1920×1080, 25 fps). The mp4 is gitignored: it is uploaded to GitHub and linked from the
README instead.

## Cost

One live run makes four Gemini generation calls (the suggested questions after the
upload, on a lite model; the PDF answer; the chat answer; the image answer), a few
embedding calls, and one Cloudflare image (57.6 of the 10,000 free daily neurons).

The committed assets were recorded on 2026-10-31 against
https://visionaryx-dusky.vercel.app: 78.7 s, nothing still for longer than a hold. The
models word their answers afresh on every run, so a new recording will differ in wording.
