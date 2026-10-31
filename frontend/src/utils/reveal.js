// The whole answer has already arrived; this only animates it. A fixed delay per word
// made a 400-word answer take ~7 s to appear, so the reveal is capped at maxMs (R6).
export const REVEAL_MS = 1000;
const MAX_STEPS = 40;
const MAX_STEP_DELAY = 25;

export async function reveal(text, onUpdate, maxMs = REVEAL_MS) {
  const words = text.split(" ");
  const steps = Math.min(words.length, MAX_STEPS);
  const wordsPerStep = Math.ceil(words.length / steps);
  const delay = Math.min(MAX_STEP_DELAY, maxMs / steps);
  for (let shown = wordsPerStep; shown < words.length; shown += wordsPerStep) {
    onUpdate(words.slice(0, shown).join(" "));
    await new Promise((r) => setTimeout(r, delay));
  }
  onUpdate(text);
}
