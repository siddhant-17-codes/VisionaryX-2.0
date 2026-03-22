import client from "./client";
export const sendMessage = (message, history) =>
  client.post("/api/chat", { message, history }).then((r) => r.data.reply);
