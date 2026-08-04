import { useEffect, useState } from "react";

function ProductForm({
  product,
  onSubmit,
  onCancel,
}) {
  const [formData, setFormData] = useState({
    name: "",
    sku: "",
    description: "",
    purchase_price: "",
    sale_price: "",
    current_stock: "",
    minimum_stock_level: "",
    expiry_date: "",
  });

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name || "",
        sku: product.sku || "",
        description: product.description || "",
        purchase_price:
          product.purchase_price || "",
        sale_price:
          product.sale_price || "",
        current_stock:
          product.current_stock || "",
        minimum_stock_level:
          product.minimum_stock_level || "",
        expiry_date:
          product.expiry_date || "",
      });
    }
  }, [product]);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    onSubmit({
      ...formData,
      purchase_price: Number(
        formData.purchase_price
      ),
      sale_price: Number(
        formData.sale_price
      ),
      current_stock: Number(
        formData.current_stock
      ),
      minimum_stock_level: Number(
        formData.minimum_stock_level
      ),
    });
  };

  return (
    <div className="product-form-card">
      <div className="form-header">
        <h2>
          {product
            ? "Edit Product"
            : "Add New Product"}
        </h2>

        <button
          type="button"
          onClick={onCancel}
          className="close-button"
        >
          ×
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label>Product Name</label>

            <input
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter product name"
              required
            />
          </div>

          <div className="form-group">
            <label>SKU</label>

            <input
              name="sku"
              value={formData.sku}
              onChange={handleChange}
              placeholder="Enter SKU"
              required
            />
          </div>

          <div className="form-group">
            <label>Purchase Price</label>

            <input
              type="number"
              step="0.01"
              name="purchase_price"
              value={
                formData.purchase_price
              }
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Selling Price</label>

            <input
              type="number"
              step="0.01"
              name="sale_price"
              value={
                formData.sale_price
              }
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Current Stock</label>

            <input
              type="number"
              name="current_stock"
              value={
                formData.current_stock
              }
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Minimum Stock Level</label>

            <input
              type="number"
              name="minimum_stock_level"
              value={
                formData.minimum_stock_level
              }
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Expiry Date</label>

            <input
              type="date"
              name="expiry_date"
              value={formData.expiry_date}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Description</label>

          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Product description"
            rows="4"
          />
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={onCancel}
            className="secondary-button"
          >
            Cancel
          </button>

          <button
            type="submit"
            className="primary-button"
          >
            {product
              ? "Update Product"
              : "Create Product"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ProductForm;