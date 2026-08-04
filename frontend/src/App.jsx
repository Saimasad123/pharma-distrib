import { useEffect, useState } from "react";

import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";

import Dashboard from "./pages/Dashboard";
import Customers from "./pages/Customers";
import Products from "./pages/Products";
import Purchases from "./pages/Purchases";
import Suppliers from "./pages/Suppliers";
import SalesOrders from "./pages/SalesOrders";
import Inventory from "./pages/Inventory";
import Reports from "./pages/Reports";
import Analytics from "./pages/Analytics";
import Login from "./pages/Login";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() =>
    Boolean(localStorage.getItem("access_token"))
  );
  const [currentPath, setCurrentPath] = useState(window.location.pathname || "/");

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname || "/");
    };

    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);

  const navigateTo = (path) => {
    window.history.pushState({}, "", path);
    setCurrentPath(path);
  };

  const handleLogin = () => {
    setIsAuthenticated(true);
    navigateTo("/");
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setIsAuthenticated(false);
    navigateTo("/");
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  const renderPage = () => {
    switch (currentPath) {
      case "/products":
        return <Products />;
      case "/customers":
        return <Customers />;
      case "/suppliers":
        return <Suppliers />;
      case "/purchases":
        return <Purchases />;
      case "/sales-orders":
        return <SalesOrders />;
      case "/inventory":
        return <Inventory />;
      case "/reports":
        return <Reports />;
      case "/analytics":
        return <Analytics />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Sidebar onNavigate={navigateTo} />

      <div className="main-area">
        <Navbar onLogout={handleLogout} />

        <main className="main-content">{renderPage()}</main>
      </div>
    </div>
  );
}

export default App;