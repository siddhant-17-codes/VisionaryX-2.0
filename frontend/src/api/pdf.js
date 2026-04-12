import client from "./client";

export const uploadPDFs = (files, chatSessionId = null) => {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  if (chatSessionId) {
    form.append("chat_session_id", chatSessionId);
  }
  return client.post("/api/pdf/upload", form).then((r) => r.data);
};

export const queryPDF = (sessionId, question, history = [], chatSessionId = null) =>
  client
    .post("/api/pdf/query", {
      session_id: sessionId,
      question,
      history,
      chat_session_id: chatSessionId,
    })
    .then((r) => r.data);