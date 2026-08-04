import apiClient from "./client";

export const getSuppliers = async () => {
  const response = await apiClient.get(
    "/suppliers"
  );

  return response.data;
};

export const getSupplier = async (
  supplierId
) => {
  const response = await apiClient.get(
    `/suppliers/${supplierId}`
  );

  return response.data;
};

export const createSupplier = async (
  data
) => {
  const response = await apiClient.post(
    "/suppliers",
    data
  );

  return response.data;
};

export const updateSupplier = async (
  supplierId,
  data
) => {
  const response = await apiClient.put(
    `/suppliers/${supplierId}`,
    data
  );

  return response.data;
};

export const deleteSupplier = async (
  supplierId
) => {
  await apiClient.delete(
    `/suppliers/${supplierId}`
  );
};