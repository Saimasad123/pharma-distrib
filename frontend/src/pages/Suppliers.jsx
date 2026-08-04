import { useEffect, useState } from "react";

import {
  getSuppliers,
  createSupplier,
  updateSupplier,
  deleteSupplier,
} from "../api/supplier";

import SupplierForm from "../components/SupplierForm";


function Suppliers() {
  const [suppliers, setSuppliers] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [showForm, setShowForm] =
    useState(false);

  const [editingSupplier, setEditingSupplier] =
    useState(null);


  // =====================================================
  // LOAD SUPPLIERS
  // =====================================================

  const loadSuppliers = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getSuppliers();

      setSuppliers(data);

    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Failed to load suppliers."
      );

    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    loadSuppliers();
  }, []);


  // =====================================================
  // CREATE SUPPLIER
  // =====================================================

  const handleCreate = async (data) => {
    try {

      await createSupplier(data);

      setShowForm(false);

      await loadSuppliers();

    } catch (err) {

      alert(
        err.response?.data?.detail ||
          "Failed to create supplier."
      );

    }
  };


  // =====================================================
  // UPDATE SUPPLIER
  // =====================================================

  const handleUpdate = async (data) => {
    try {

      await updateSupplier(
        editingSupplier.id,
        data
      );

      setEditingSupplier(null);

      setShowForm(false);

      await loadSuppliers();

    } catch (err) {

      alert(
        err.response?.data?.detail ||
          "Failed to update supplier."
      );

    }
  };


  // =====================================================
  // DELETE SUPPLIER
  // =====================================================

  const handleDelete = async (
    supplierId
  ) => {

    const confirmed = window.confirm(
      "Are you sure you want to delete this supplier?"
    );

    if (!confirmed) {
      return;
    }

    try {

      await deleteSupplier(
        supplierId
      );

      await loadSuppliers();

    } catch (err) {

      alert(
        err.response?.data?.detail ||
          "Failed to delete supplier."
      );

    }
  };


  // =====================================================
  // OPEN CREATE FORM
  // =====================================================

  const openCreateForm = () => {

    setEditingSupplier(null);

    setShowForm(true);

  };


  // =====================================================
  // OPEN EDIT FORM
  // =====================================================

  const openEditForm = (
    supplier
  ) => {

    setEditingSupplier(
      supplier
    );

    setShowForm(true);

  };


  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {

    return (
      <div className="page-loading">
        Loading suppliers...
      </div>
    );

  }


  // =====================================================
  // PAGE
  // =====================================================

  return (

    <div className="products-page">

      <div className="page-header">

        <div>

          <h1>
            Suppliers
          </h1>

          <p>
            Manage your pharmaceutical
            suppliers.
          </p>

        </div>


        <button
          className="primary-button"
          onClick={
            openCreateForm
          }
        >
          + Add Supplier
        </button>

      </div>


      {error && (

        <div className="dashboard-error">
          {error}
        </div>

      )}


      {showForm && (

        <SupplierForm
          supplier={
            editingSupplier
          }

          onSubmit={
            editingSupplier
              ? handleUpdate
              : handleCreate
          }

          onCancel={() => {

            setShowForm(false);

            setEditingSupplier(
              null
            );

          }}
        />

      )}


      <div className="products-card">

        <div className="table-wrapper">

          <table className="products-table">

            <thead>

              <tr>

                <th>
                  Supplier
                </th>

                <th>
                  Contact Person
                </th>

                <th>
                  Phone
                </th>

                <th>
                  Email
                </th>

                <th>
                  Tax Number
                </th>

                <th>
                  Address
                </th>

                <th>
                  Actions
                </th>

              </tr>

            </thead>


            <tbody>

              {suppliers.length === 0 ? (

                <tr>

                  <td
                    colSpan="7"
                    className="empty-state"
                  >
                    No suppliers found.
                  </td>

                </tr>

              ) : (

                suppliers.map(
                  (supplier) => (

                    <tr
                      key={
                        supplier.id
                      }
                    >

                      <td>

                        <strong>
                          {
                            supplier.name
                          }
                        </strong>

                      </td>


                      <td>

                        {
                          supplier.contact_person ||
                          "N/A"
                        }

                      </td>


                      <td>

                        {
                          supplier.phone ||
                          "N/A"
                        }

                      </td>


                      <td>

                        {
                          supplier.email ||
                          "N/A"
                        }

                      </td>


                      <td>

                        {
                          supplier.tax_number ||
                          "N/A"
                        }

                      </td>


                      <td>

                        {
                          supplier.address ||
                          "N/A"
                        }

                      </td>


                      <td>

                        <div className="action-buttons">

                          <button
                            className="edit-button"
                            onClick={() =>
                              openEditForm(
                                supplier
                              )
                            }
                          >
                            Edit
                          </button>


                          <button
                            className="delete-button"
                            onClick={() =>
                              handleDelete(
                                supplier.id
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


export default Suppliers;