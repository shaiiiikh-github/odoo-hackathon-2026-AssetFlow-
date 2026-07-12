import axios from "axios";

export const httpClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

httpClient.interceptors.response.use(
  (response) => response,
  (error) =>
    Promise.reject({
      message:
        error.response?.data?.message ||
        error.message ||
        "The request could not be completed.",
      status: error.response?.status,
      data: error.response?.data,
    }),
);
