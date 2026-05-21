import axios from "axios";
import { auth } from "@/auth";

const baseURL =
  process.env.NODE_ENV === "development"
    ? "http://localhost:4000/api/v1"
    : "http://nginx:80/api/v1";

export async function getApiServer() {
  const session = await auth();

  const instance = axios.create({
    baseURL,
  });

  instance.interceptors.request.use((config) => {
    if (session?.accessToken) {
      config.headers.Authorization = `Bearer ${session.accessToken}`;
    }
    return config;
  });

  return instance;
}
