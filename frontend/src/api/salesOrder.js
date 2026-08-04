import apiClient from "./client";

export const getSalesOrders = async () => {
  const response = await apiClient.get("/sales-orders");
  return response.data;
};

export const createSalesOrder = async (data) => {
  const response = await apiClient.post(
    "/sales-orders",
    data
  );
  return response.data;
};

export const confirmSalesOrder = async (orderId) => {
  const response = await apiClient.post(
    `/sales-orders/${orderId}/confirm`
  );
  return response.data;
};
