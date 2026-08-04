import { useEffect, useState } from "react";

import {
  getCustomers,
  createCustomer,
  updateCustomer,
  deleteCustomer,
} from "../api/customer";

import CustomerForm from "../components/CustomerForm";

function Customers() {
  const [customers, setCustomers] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [showForm, setShowForm] =
    useState(false);

  const [editingCustomer, setEditingCustomer] =
    useState(null);

  const loadCustomers = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getCustomers();

      setCustomers(data);
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Failed to load customers."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCustomers();
  }, []);

  const handleCreate = async (data) => {
    try {
      await createCustomer(data);

      setShowForm(false);

      await loadCustomers();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to create customer."
      );
    }
  };

  const handleUpdate = async (data) => {
    try {
      await updateCustomer(
        editingCustomer.id,
        data
      );

      setEditingCustomer(null);
      setShowForm(false);

      await loadCustomers();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to update customer."
      );
    }
  };

  const handleDelete = async (
    customerId
  ) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this customer?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await deleteCustomer(customerId);

      await loadCustomers();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to delete customer."
      );
    }
  };

  const openCreateForm = () => {
    setEditingCustomer(null);
    setShowForm(true);
  };

  const openEditForm = (customer) => {
    setEditingCustomer(customer);
    setShowForm(true);
  };

  if (loading) {
    return (
      <div className="page-loading">
        Loading customers...
      </div>
    );
  }

  return (
    <div className="products-page">
      <div className="page-header">
        <div>
          <h1>Customers</h1>

          <p>
            Manage your pharmaceutical
            customers.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={openCreateForm}
        >
          + Add Customer
        </button>
      </div>

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      {showForm && (
        <CustomerForm
          customer={editingCustomer}
          onSubmit={
            editingCustomer
              ? handleUpdate
              : handleCreate
          }
          onCancel={() => {
            setShowForm(false);
            setEditingCustomer(null);
          }}
        />
      )}

      <div className="products-card">
        <div className="table-wrapper">
          <table className="products-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Contact Person</th>
                <th>Phone</th>
                <th>Email</th>
                <th>Tax Number</th>
                <th>Address</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {customers.length === 0 ? (
                <tr>
                  <td
                    colSpan="7"
                    className="empty-state"
                  >
                    No customers found.
                  </td>
                </tr>
              ) : (
                customers.map(
                  (customer) => (
                    <tr
                      key={customer.id}
                    >
                      <td>
                        <strong>
                          {customer.name}
                        </strong>
                      </td>

                      <td>
                        {customer.contact_person ||
                          "N/A"}
                      </td>

                      <td>
                        {customer.phone ||
                          "N/A"}
                      </td>

                      <td>
                        {customer.email ||
                          "N/A"}
                      </td>

                      <td>
                        {customer.tax_number ||
                          "N/A"}
                      </td>

                      <td>
                        {customer.address ||
                          "N/A"}
                      </td>

                      <td>
                        <div className="action-buttons">
                          <button
                            className="edit-button"
                            onClick={() =>
                              openEditForm(
                                customer
                              )
                            }
                          >
                            Edit
                          </button>

                          <button
                            className="delete-button"
                            onClick={() =>
                              handleDelete(
                                customer.id
                              )
                            }
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                )
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Customers;