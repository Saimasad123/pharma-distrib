import { useEffect, useState } from "react";
import {
  getSalesOrders,
  createSalesOrder,
  confirmSalesOrder,
} from "../api/salesOrder";
import { getCustomers } from "../api/customer";
import { getProducts } from "../api/product";

function SalesOrders() {
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [orderNumber, setOrderNumber] = useState("");
  const [customerId, setCustomerId] = useState("");
  const [notes, setNotes] = useState("");
  const [items, setItems] = useState([
    { product_id: "", quantity: 1 },
  ]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const [ordersData, customersData, productsData] = await Promise.all([
        getSalesOrders(),
        getCustomers(),
        getProducts(),
      ]);

      setOrders(ordersData);
      setCustomers(customersData);
      setProducts(productsData);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
          "Failed to load sales orders."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const resetForm = () => {
    setOrderNumber("");
    setCustomerId("");
    setNotes("");
    setItems([{ product_id: "", quantity: 1 }]);
  };

  const handleAddItem = () => {
    setItems([...items, { product_id: "", quantity: 1 }]);
  };

  const handleRemoveItem = (index) => {
    if (items.length === 1) {
      return;
    }

    setItems(items.filter((_, idx) => idx !== index));
  };

  const handleItemChange = (index, field, value) => {
    const updated = [...items];
    updated[index] = {
      ...updated[index],
      [field]: field === "quantity" ? Number(value) : value,
    };
    setItems(updated);
  };

  const handleCreateOrder = async (event) => {
    event.preventDefault();

    if (!customerId) {
      alert("Please select a customer.");
      return;
    }

    if (!orderNumber.trim()) {
      alert("Please enter an order number.");
      return;
    }

    if (items.some((item) => !item.product_id || item.quantity <= 0)) {
      alert(
        "Please add at least one product with a valid quantity."
      );
      return;
    }

    try {
      await createSalesOrder({
        customer_id: customerId,
        order_number: orderNumber.trim(),
        notes: notes.trim() || null,
        items,
      });

      setShowForm(false);
      resetForm();
      await loadData();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to create sales order."
      );
    }
  };

  const handleConfirmOrder = async (orderId) => {
    const confirmed = window.confirm(
      "Confirm this sales order and reduce stock?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await confirmSalesOrder(orderId);
      await loadData();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to confirm sales order."
      );
    }
  };

  if (loading) {
    return (
      <div className="page-loading">
        Loading sales orders...
      </div>
    );
  }

  return (
    <div className="products-page">
      <div className="page-header">
        <div>
          <h1>Sales Orders</h1>
          <p>Manage customer sales orders and confirmations.</p>
        </div>

        <button
          className="primary-button"
          onClick={() => setShowForm(true)}
        >
          + New Sales Order
        </button>
      </div>

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      {showForm && (
        <div className="product-form-card">
          <div className="form-header">
            <h2>Create Sales Order</h2>
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                resetForm();
              }}
              className="close-button"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleCreateOrder}>
            <div className="form-grid">
              <div className="form-group">
                <label>Order Number</label>
                <input
                  value={orderNumber}
                  onChange={(event) =>
                    setOrderNumber(event.target.value)
                  }
                  placeholder="Enter order number"
                  required
                />
              </div>

              <div className="form-group">
                <label>Customer</label>
                <select
                  value={customerId}
                  onChange={(event) =>
                    setCustomerId(event.target.value)
                  }
                  required
                >
                  <option value="">Select customer</option>
                  {customers.map((customer) => (
                    <option key={customer.id} value={customer.id}>
                      {customer.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group full-width">
                <label>Notes</label>
                <textarea
                  value={notes}
                  onChange={(event) =>
                    setNotes(event.target.value)
                  }
                  placeholder="Optional order notes"
                  rows="3"
                />
              </div>
            </div>

            <div className="form-divider" />

            <div className="form-group full-width">
              <h3>Order Items</h3>
            </div>

            {items.map((item, index) => (
              <div key={index} className="form-grid item-row">
                <div className="form-group">
                  <label>Product</label>
                  <select
                    value={item.product_id}
                    onChange={(event) =>
                      handleItemChange(
                        index,
                        "product_id",
                        event.target.value
                      )
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
                  <label>Quantity</label>
                  <input
                    type="number"
                    min="1"
                    value={item.quantity}
                    onChange={(event) =>
                      handleItemChange(
                        index,
                        "quantity",
                        event.target.value
                      )
                    }
                    required
                  />
                </div>

                <div className="form-group action-column">
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => handleRemoveItem(index)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={handleAddItem}
              >
                + Add Item
              </button>

              <button type="submit" className="primary-button">
                Create Order
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="products-card">
        <div className="table-wrapper">
          <table className="products-table">
            <thead>
              <tr>
                <th>Order #</th>
                <th>Customer</th>
                <th>Status</th>
                <th>Total</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.length === 0 ? (
                <tr>
                  <td colSpan="6" className="empty-state">
                    No sales orders found.
                  </td>
                </tr>
              ) : (
                orders.map((order) => {
                  const customer = customers.find(
                    (item) => item.id === order.customer_id
                  );

                  return (
                    <tr key={order.id}>
                      <td>
                        <strong>{order.order_number}</strong>
                      </td>
                      <td>{customer?.name || "Unknown"}</td>
                      <td>{order.status}</td>
                      <td>
                        Rs. {Number(order.total_amount).toLocaleString()}
                      </td>
                      <td>{new Date(order.created_at).toLocaleDateString()}</td>
                      <td>
                        {order.status === "PENDING" ? (
                          <button
                            className="primary-button"
                            onClick={() => handleConfirmOrder(order.id)}
                          >
                            Confirm
                          </button>
                        ) : (
                          <span className="status-badge status-confirmed">
                            Confirmed
                          </span>
                        )}
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

export default SalesOrders;
