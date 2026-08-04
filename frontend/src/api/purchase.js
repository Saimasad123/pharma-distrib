import apiClient from "./client";

// Get all purchases
export const getPurchases = async () => {
  const response = await apiClient.get("/purchases");
  return response.data;
};

// Get one purchase
export const getPurchase = async (purchaseId) => {
  const response = await apiClient.get(
    `/purchases/${purchaseId}`
  );
  return response.data;
};

// Create purchase
export const createPurchase = async (data) => {
  const response = await apiClient.post(
    "/purchases",
    data
  );
  return response.data;
};

// Receive purchase
export const receivePurchase = async (purchaseId) => {
  const response = await apiClient.post(
    `/purchases/${purchaseId}/receive`
  );
  return response.data;
};