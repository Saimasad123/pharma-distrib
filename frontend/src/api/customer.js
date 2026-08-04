import apiClient from "./client";

export const getCustomers = async () => {
  const response = await apiClient.get("/customers");
  return response.data;
};

export const getCustomer = async (customerId) => {
  const response = await apiClient.get(
    `/customers/${customerId}`
  );

  return response.data;
};

export const createCustomer = async (data) => {
  const response = await apiClient.post(
    "/customers",
    data
  );

  return response.data;
};

export const updateCustomer = async (
  customerId,
  data
) => {
  const response = await apiClient.put(
    `/customers/${customerId}`,
    data
  );

  return response.data;
};

export const deleteCustomer = async (
  customerId
) => {
  await apiClient.delete(
    `/customers/${customerId}`
  );
};