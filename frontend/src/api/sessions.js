import client from "./client";

export const createSession = (mode = "chat", title = "New chat") =>
  client.post("/api/sessions", { mode, title }).then((r) => r.data);

export const listSessions = () =>
  client.get("/api/sessions").then((r) => r.data);

export const getSession = (id) =>
  client.get(`/api/sessions/${id}`).then((r) => r.data);

export const deleteSession = (id) =>
  client.delete(`/api/sessions/${id}`).then((r) => r.data);
