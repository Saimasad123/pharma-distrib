import { useEffect, useState } from "react";
import { getDashboard } from "../api/dashboard";
import StatCard from "../components/StatCard";

function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const data = await getDashboard();
        setDashboard(data);
      } catch (err) {
        console.error("Dashboard error:", err);

        setError(
          err.response?.data?.detail ||
          "Failed to load dashboard data."
        );
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-loading">
        Loading dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        {error}
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p>
            Welcome back! Here's what's happening
            with your business.
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Total Products"
          value={dashboard.total_products}
          icon="📦"
          description="Active products"
        />

        <StatCard
          title="Total Customers"
          value={dashboard.total_customers}
          icon="👥"
          description="Active customers"
        />

        <StatCard
          title="Total Suppliers"
          value={dashboard.total_suppliers}
          icon="🏭"
          description="Active suppliers"
        />

        <StatCard
          title="Sales Orders"
          value={dashboard.total_sales_orders}
          icon="📋"
          description={`${dashboard.confirmed_sales_orders} confirmed`}
        />

        <StatCard
          title="Total Revenue"
          value={`Rs. ${Number(
            dashboard.total_revenue
          ).toLocaleString()}`}
          icon="💰"
          description="Total sales revenue"
        />

        <StatCard
          title="Total Profit"
          value={`Rs. ${Number(
            dashboard.total_profit
          ).toLocaleString()}`}
          icon="📈"
          description="Net profit"
        />
      </div>

      <div className="dashboard-sections">
        <div className="inventory-card">
          <h2>Inventory Overview</h2>

          <div className="inventory-stats">
            <div>
              <span>Inventory Value</span>
              <strong>
                Rs.{" "}
                {Number(
                  dashboard.total_inventory_value
                ).toLocaleString()}
              </strong>
            </div>

            <div>
              <span>Low Stock</span>
              <strong>
                {dashboard.low_stock_products}
              </strong>
            </div>

            <div>
              <span>Expired Products</span>
              <strong>
                {dashboard.expired_products}
              </strong>
            </div>
          </div>
        </div>

        <div className="orders-card">
          <h2>Order Overview</h2>

          <div className="order-stats">
            <div>
              <span>Total Orders</span>
              <strong>
                {dashboard.total_sales_orders}
              </strong>
            </div>

            <div>
              <span>Pending</span>
              <strong>
                {dashboard.pending_sales_orders}
              </strong>
            </div>

            <div>
              <span>Confirmed</span>
              <strong>
                {dashboard.confirmed_sales_orders}
              </strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;