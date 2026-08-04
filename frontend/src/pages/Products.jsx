import { useEffect, useState } from "react";

import {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
} from "../api/product";

import ProductForm from "../components/ProductForm";

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] =
    useState(null);

  const loadProducts = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getProducts();

      setProducts(data);
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Failed to load products."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleCreate = async (data) => {
    try {
      await createProduct(data);

      setShowForm(false);

      await loadProducts();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to create product."
      );
    }
  };

  const handleUpdate = async (data) => {
    try {
      await updateProduct(
        editingProduct.id,
        data
      );

      setEditingProduct(null);

      setShowForm(false);

      await loadProducts();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to update product."
      );
    }
  };

  const handleDelete = async (productId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this product?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await deleteProduct(productId);

      await loadProducts();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to delete product."
      );
    }
  };

  const openCreateForm = () => {
    setEditingProduct(null);
    setShowForm(true);
  };

  const openEditForm = (product) => {
    setEditingProduct(product);
    setShowForm(true);
  };

  if (loading) {
    return (
      <div className="page-loading">
        Loading products...
      </div>
    );
  }

  return (
    <div className="products-page">
      <div className="page-header">
        <div>
          <h1>Products</h1>

          <p>
            Manage your pharmaceutical inventory.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={openCreateForm}
        >
          + Add Product
        </button>
      </div>

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      {showForm && (
        <ProductForm
          product={editingProduct}
          onSubmit={
            editingProduct
              ? handleUpdate
              : handleCreate
          }
          onCancel={() => {
            setShowForm(false);
            setEditingProduct(null);
          }}
        />
      )}

      <div className="products-card">
        <div className="table-wrapper">
          <table className="products-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>SKU</th>
                <th>Purchase Price</th>
                <th>Selling Price</th>
                <th>Stock</th>
                <th>Expiry</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {products.length === 0 ? (
                <tr>
                  <td
                    colSpan="7"
                    className="empty-state"
                  >
                    No products found.
                  </td>
                </tr>
              ) : (
                products.map((product) => (
                  <tr key={product.id}>
                    <td>
                      <strong>
                        {product.name}
                      </strong>
                    </td>

                    <td>{product.sku}</td>

                    <td>
                      Rs.{" "}
                      {Number(
                        product.purchase_price
                      ).toLocaleString()}
                    </td>

                    <td>
                      Rs.{" "}
                      {Number(
                        product.sale_price
                      ).toLocaleString()}
                    </td>

                    <td>
                      <span
                        className={
                          product.current_stock <=
                          product.minimum_stock_level
                            ? "stock-low"
                            : "stock-normal"
                        }
                      >
                        {product.current_stock}
                      </span>
                    </td>

                    <td>
                      {product.expiry_date ||
                        "N/A"}
                    </td>

                    <td>
                      <div className="action-buttons">
                        <button
                          className="edit-button"
                          onClick={() =>
                            openEditForm(product)
                          }
                        >
                          Edit
                        </button>

                        <button
                          className="delete-button"
                          onClick={() =>
                            handleDelete(
                              product.id
                            )
                          }
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Products;