"use client";

import axios from "axios";
import { getSession } from "next-auth/react";

const baseURL =
  process.env.NODE_ENV === "development"
    ? "http://localhost:4000/api/v1"
    : "/api/v1";

const apiClient = axios.create({
  baseURL,
});

apiClient.interceptors.request.use(async (config) => {
  const session = await getSession();
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`;
  }
  return config;
});

export default apiClient;
