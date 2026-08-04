import apiClient from "./client";

export const getProducts = async () => {
  const response = await apiClient.get("/products");
  return response.data;
};

export const createProduct = async (productData) => {
  const response = await apiClient.post(
    "/products",
    productData
  );

  return response.data;
};

export const updateProduct = async (
  productId,
  productData
) => {
  const response = await apiClient.put(
    `/products/${productId}`,
    productData
  );

  return response.data;
};

export const deleteProduct = async (productId) => {
  await apiClient.delete(
    `/products/${productId}`
  );
};