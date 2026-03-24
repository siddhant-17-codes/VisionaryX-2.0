import client from "./client";

export const sendMessage = (message, history = [], chatSessionId = null) =>
  client
    .post("/api/chat", {
      message,
      history,
      chat_session_id: chatSessionId,
    })
    .then((r) => r.data.reply);
