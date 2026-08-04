function Navbar({ onLogout }) {
  return (
    <header className="navbar">
      <div className="navbar-left">
        <h2>Dashboard</h2>
      </div>

      <div className="navbar-right">
        <div className="user-info">
          <div className="user-avatar">
            U
          </div>

          <div>
            <p className="user-name">
              User
            </p>

            <p className="user-role">
              Administrator
            </p>
          </div>
        </div>

        <button
          className="logout-button"
          onClick={onLogout}
        >
          Logout
        </button>
      </div>
    </header>
  );
}

export default Navbar;