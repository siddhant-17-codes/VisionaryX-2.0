import axios from "axios";
import { getClientId } from "../utils/clientId";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 120000,
});

client.interceptors.request.use((config) => {
  config.headers["X-Client-Id"] = getClientId();
  return config;
});

/** What every failed API call rejects with. `status` is 0 when no response arrived
 *  (server unreachable, asleep, or blocked by CORS); `type` is the backend's error
 *  class, or "Timeout" / "NetworkError" when there was no response. */
export class ApiError extends Error {
  constructor(message, { status = 0, type = "NetworkError", retryAfter = null } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.type = type;
    this.retryAfter = retryAfter;
  }
}

export function toApiError(err) {
  if (err.response) {
    const { status, data, headers } = err.response;
    const retryAfter = Number(headers?.["retry-after"]) || null;
    const message = data?.error || data?.detail || "Something went wrong. Please try again.";
    return new ApiError(typeof message === "string" ? message : "Something went wrong. Please try again.",
                        { status, type: data?.type || "HttpError", retryAfter });
  }
  if (err.code === "ECONNABORTED" || err.code === "ETIMEDOUT") {
    return new ApiError("The server took too long to answer.", { type: "Timeout" });
  }
  return new ApiError("Could not reach the server.");
}

client.interceptors.response.use((res) => res, (err) => Promise.reject(toApiError(err)));

export default client;
