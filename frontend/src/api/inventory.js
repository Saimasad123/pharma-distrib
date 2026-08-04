import apiClient from "./client";

export const getInventoryTransactions = async () => {
  const response = await apiClient.get(
    "/inventory/transactions"
  );
  return response.data;
};

export const createInventoryTransaction = async (data) => {
  const response = await apiClient.post(
    "/inventory/transactions",
    data
  );
  return response.data;
};

export const getProductInventoryHistory = async (productId) => {
  const response = await apiClient.get(
    `/inventory/transactions/${productId}`
  );
  return response.data;
};
