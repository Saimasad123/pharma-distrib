function Sidebar({ onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h2>PharmaDistrib</h2>
      </div>

      <nav className="sidebar-nav">
        <a href="/" onClick={(event) => {
          event.preventDefault();
          onNavigate("/");
        }}>
          Dashboard
        </a>

        <a href="/products" onClick={(event) => {
          event.preventDefault();
          onNavigate("/products");
        }}>
          Products
        </a>

        <a href="/customers" onClick={(event) => {
          event.preventDefault();
          onNavigate("/customers");
        }}>
          Customers
        </a>

        <a href="/suppliers" onClick={(event) => {
          event.preventDefault();
          onNavigate("/suppliers");
        }}>
          Suppliers
        </a>

        <a href="/purchases" onClick={(event) => {
          event.preventDefault();
          onNavigate("/purchases");
        }}>
          Purchases
        </a>

        <a href="/sales-orders" onClick={(event) => {
          event.preventDefault();
          onNavigate("/sales-orders");
        }}>
          Sales Orders
        </a>

        <a href="/inventory" onClick={(event) => {
          event.preventDefault();
          onNavigate("/inventory");
        }}>
          Inventory
        </a>

        <a href="/reports" onClick={(event) => {
          event.preventDefault();
          onNavigate("/reports");
        }}>
          Reports
        </a>

        <a href="/analytics" onClick={(event) => {
          event.preventDefault();
          onNavigate("/analytics");
        }}>
          Analytics
        </a>
      </nav>
    </aside>
  );
}

export default Sidebar;