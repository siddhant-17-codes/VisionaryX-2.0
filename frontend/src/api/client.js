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

client.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.error ||
      err.response?.data?.detail ||
      "Something went wrong. Please try again.";
    return Promise.reject(new Error(message));
  }
);

export default client;
