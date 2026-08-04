import { useEffect, useState } from "react";
import {
  getInventoryAnalytics,
  getMonthlySalesAnalytics,
  getTopProductsAnalytics,
  getTopCustomersAnalytics,
} from "../api/analytics";

function Analytics() {
  const currentYear = new Date().getFullYear();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [year, setYear] = useState(currentYear);
  const [inventoryAnalytics, setInventoryAnalytics] = useState(null);
  const [monthlySales, setMonthlySales] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [topCustomers, setTopCustomers] = useState([]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError("");

      const [inventoryData, topProductsData, topCustomersData, monthlyData] =
        await Promise.all([
          getInventoryAnalytics(),
          getTopProductsAnalytics(),
          getTopCustomersAnalytics(),
          getMonthlySalesAnalytics(year),
        ]);

      setInventoryAnalytics(inventoryData);
      setTopProducts(topProductsData.top_products || []);
      setTopCustomers(topCustomersData.top_customers || []);
      setMonthlySales(monthlyData.monthly_sales || []);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
          "Failed to load analytics."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, [year]);

  if (loading) {
    return (
      <div className="page-loading">
        Loading analytics...
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Analytics</h1>
          <p>View sales and inventory trends for your business.</p>
        </div>

        <div className="filter-row">
          <label>
            Year
            <input
              type="number"
              min="2000"
              max="2100"
              value={year}
              onChange={(event) => setYear(Number(event.target.value))}
            />
          </label>
        </div>
      </div>

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Inventory Value</h3>
          <p>
            Rs. {Number(inventoryAnalytics?.total_inventory_value || 0).toLocaleString()}
          </p>
          <p>Stock units: {inventoryAnalytics?.total_stock_units || 0}</p>
          <p>Low stock: {inventoryAnalytics?.low_stock_products || 0}</p>
          <p>Expired: {inventoryAnalytics?.expired_products || 0}</p>
        </div>

        <div className="stat-card">
          <h3>Top Products</h3>
          {topProducts.length === 0 ? (
            <p>No top products yet.</p>
          ) : (
            <ul className="analytics-list">
              {topProducts.slice(0, 5).map((product) => (
                <li key={product.product_id}>
                  <strong>{product.product_name}</strong> — {product.quantity_sold} sold
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="stat-card">
          <h3>Top Customers</h3>
          {topCustomers.length === 0 ? (
            <p>No top customers yet.</p>
          ) : (
            <ul className="analytics-list">
              {topCustomers.slice(0, 5).map((customer) => (
                <li key={customer.customer_id}>
                  <strong>{customer.customer_name}</strong> — Rs. {Number(customer.total_spending || 0).toLocaleString()}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="products-card">
        <div className="table-wrapper">
          <table className="products-table">
            <thead>
              <tr>
                <th>Month</th>
                <th>Revenue</th>
                <th>Cost</th>
                <th>Profit</th>
                <th>Orders</th>
              </tr>
            </thead>
            <tbody>
              {monthlySales.length === 0 ? (
                <tr>
                  <td colSpan="5" className="empty-state">
                    No monthly sales analytics found.
                  </td>
                </tr>
              ) : (
                monthlySales.map((item) => (
                  <tr key={item.month}>
                    <td>{new Date(0, item.month - 1).toLocaleString("default", { month: "short" })}</td>
                    <td>Rs. {Number(item.revenue || 0).toLocaleString()}</td>
                    <td>Rs. {Number(item.cost || 0).toLocaleString()}</td>
                    <td>Rs. {Number(item.profit || 0).toLocaleString()}</td>
                    <td>{item.orders || 0}</td>
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

export default Analytics;
