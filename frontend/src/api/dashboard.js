import apiClient from "./client";

export const getDashboard = async () => {
  const response = await apiClient.get("/dashboard");
  return response.data;
};