import axios from "axios";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
  timeout: 60000,
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.detail || "Something went wrong. Please try again.";
    return Promise.reject(new Error(message));
  }
);

export default client;
