import apiClient from "./client";

export const getInventoryAnalytics = async () => {
  const response = await apiClient.get("/analytics/inventory");
  return response.data;
};

export const getTopProductsAnalytics = async (limit = 10) => {
  const response = await apiClient.get("/analytics/top-products", {
    params: { limit },
  });
  return response.data;
};

export const getTopCustomersAnalytics = async (limit = 10) => {
  const response = await apiClient.get("/analytics/top-customers", {
    params: { limit },
  });
  return response.data;
};

export const getMonthlySalesAnalytics = async (year) => {
  const response = await apiClient.get("/analytics/monthly-sales", {
    params: { year },
  });
  return response.data;
};
