import client from "./client";

export const queryImage = (file, prompt = "") => {
  const form = new FormData();
  form.append("file", file);
  form.append("prompt", prompt || "Describe this image in detail.");
  return client.post("/api/image/query", form).then((r) => r.data); // { answer, model }
};

export const generateImage = (prompt) =>
  client.post("/api/generate/image", { prompt }).then((r) => r.data.image_base64);

// { available, resumes_at }: image generation is paused when every free quota is used up.
export const getImageStatus = () =>
  client.get("/api/generate/status").then((r) => r.data);
