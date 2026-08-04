import apiClient from "./client";

export const getProfitReport = async (params = {}) => {
  const response = await apiClient.get("/reports/profit", {
    params,
  });
  return response.data;
};

export const getRevenueReport = async (params = {}) => {
  const response = await apiClient.get("/reports/revenue", {
    params,
  });
  return response.data;
};

export const getMonthlyReport = async (year, month) => {
  const response = await apiClient.get("/reports/monthly", {
    params: { year, month },
  });
  return response.data;
};

export const getAnnualReport = async (year) => {
  const response = await apiClient.get("/reports/annual", {
    params: { year },
  });
  return response.data;
};
