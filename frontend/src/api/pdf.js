import client from "./client";

export const uploadPDFs = (files, chatSessionId = null) => {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  const url = chatSessionId
    ? `/api/pdf/upload?chat_session_id=${chatSessionId}`
    : "/api/pdf/upload";
  return client.post(url, form).then((r) => r.data);
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
