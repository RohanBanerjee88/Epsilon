export const APP_BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH ?? "").replace(/\/$/, "");

export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL
  ?? (process.env.NODE_ENV === "development" ? "http://localhost:8080" : APP_BASE_PATH)
).replace(/\/$/, "");
