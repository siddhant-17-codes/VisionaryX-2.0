import client from "./client";

export const uploadPDFs = (files) => {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  return client.post("/api/pdf/upload", form).then((r) => r.data);
};

export const queryPDF = (sessionId, question, history) =>
  client
    .post("/api/pdf/query", { session_id: sessionId, question, history })
    .then((r) => r.data);
