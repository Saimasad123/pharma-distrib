import { useEffect, useState } from "react";
import {
  getInventoryTransactions,
  createInventoryTransaction,
} from "../api/inventory";
import { getProducts } from "../api/product";

function Inventory() {
  const [transactions, setTransactions] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    product_id: "",
    transaction_type: "STOCK_IN",
    quantity: 1,
    reason: "",
    notes: "",
  });

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const [transactionsData, productsData] = await Promise.all([
        getInventoryTransactions(),
        getProducts(),
      ]);

      setTransactions(transactionsData);
      setProducts(productsData);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
          "Failed to load inventory transactions."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: field === "quantity" ? Number(value) : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!formData.product_id) {
      alert("Please select a product.");
      return;
    }

    if (formData.quantity <= 0) {
      alert("Quantity must be greater than zero.");
      return;
    }

    try {
      await createInventoryTransaction(formData);
      setFormData({
        product_id: "",
        transaction_type: "STOCK_IN",
        quantity: 1,
        reason: "",
        notes: "",
      });
      await loadData();
      alert("Inventory transaction created successfully.");
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to create inventory transaction."
      );
    }
  };

  if (loading) {
    return (
      <div className="page-loading">
        Loading inventory...
      </div>
    );
  }

  return (
    <div className="products-page">
      <div className="page-header">
        <div>
          <h1>Inventory</h1>
          <p>Track inventory transactions and stock movement.</p>
        </div>
      </div>

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      <div className="product-form-card">
        <div className="form-header">
          <h2>Create Inventory Transaction</h2>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label>Product</label>
              <select
                value={formData.product_id}
                onChange={(event) =>
                  handleChange("product_id", event.target.value)
                }
                required
              >
                <option value="">Select product</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Type</label>
              <select
                value={formData.transaction_type}
                onChange={(event) =>
                  handleChange("transaction_type", event.target.value)
                }
              >
                <option value="STOCK_IN">Stock In</option>
                <option value="STOCK_OUT">Stock Out</option>
                <option value="ADJUSTMENT">Adjustment</option>
              </select>
            </div>

            <div className="form-group">
              <label>Quantity</label>
              <input
                type="number"
                min="1"
                value={formData.quantity}
                onChange={(event) =>
                  handleChange("quantity", event.target.value)
                }
                required
              />
            </div>

            <div className="form-group full-width">
              <label>Reason</label>
              <input
                value={formData.reason}
                onChange={(event) =>
                  handleChange("reason", event.target.value)
                }
                placeholder="Reason for transaction"
              />
            </div>

            <div className="form-group full-width">
              <label>Notes</label>
              <textarea
                value={formData.notes}
                onChange={(event) =>
                  handleChange("notes", event.target.value)
                }
                placeholder="Additional notes"
                rows="3"
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="primary-button">
              Create Transaction
            </button>
          </div>
        </form>
      </div>

      <div className="products-card">
        <div className="table-wrapper">
          <table className="products-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Type</th>
                <th>Quantity</th>
                <th>Previous</th>
                <th>New Stock</th>
                <th>Reason</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan="7" className="empty-state">
                    No inventory transactions found.
                  </td>
                </tr>
              ) : (
                transactions.map((transaction) => {
                  const product = products.find(
                    (item) => item.id === transaction.product_id
                  );

                  return (
                    <tr key={transaction.id}>
                      <td>{product?.name || "Unknown"}</td>
                      <td>{transaction.transaction_type}</td>
                      <td>{transaction.quantity}</td>
                      <td>{transaction.previous_stock}</td>
                      <td>{transaction.new_stock}</td>
                      <td>{transaction.reason || "—"}</td>
                      <td>
                        {new Date(transaction.created_at).toLocaleString()}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Inventory;
