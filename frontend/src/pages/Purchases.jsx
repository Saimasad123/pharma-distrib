import { useEffect, useState } from "react";

import {
  createPurchase,
  getPurchases,
  receivePurchase,
} from "../api/purchase";
import { getSuppliers } from "../api/supplier";

import PurchaseForm from "../components/PurchaseForm";
import { formatCurrency, getPurchaseStatusClass } from "../utils/purchaseUtils";

function Purchases() {
  const [purchases, setPurchases] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [suppliers, setSuppliers] = useState([]);


  // =====================================================
  // LOAD PURCHASES
  // =====================================================

  const loadPurchases = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getPurchases();

      setPurchases(data);

    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Failed to load purchases."
      );

    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [purchasesData, suppliersData] = await Promise.all([
          getPurchases(),
          getSuppliers(),
        ]);

        setPurchases(purchasesData);
        setSuppliers(suppliersData);
      } catch (err) {
        console.error(err);
        setError(
          err.response?.data?.detail ||
            "Failed to load purchases."
        );
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, []);


  // =====================================================
  // CREATE PURCHASE
  // =====================================================

  const handleCreate = async (data) => {
    try {
      await createPurchase(data);

      setShowForm(false);

      await loadPurchases();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to create purchase."
      );
    }
  };

  // =====================================================
  // RECEIVE PURCHASE
  // =====================================================

  const handleReceive = async (purchaseId) => {

    const confirmed = window.confirm(
      "Are you sure you want to receive this purchase? Stock will be added to inventory."
    );

    if (!confirmed) {
      return;
    }

    try {

      await receivePurchase(purchaseId);

      await loadPurchases();

      alert(
        "Purchase received successfully. Inventory stock has been updated."
      );

    } catch (err) {

      console.error(err);

      alert(
        err.response?.data?.detail ||
        "Failed to receive purchase."
      );

    }
  };


  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {

    return (
      <div className="page-loading">
        Loading purchases...
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
            Purchases
          </h1>

          <p>
            Manage pharmaceutical purchases
            from your suppliers.
          </p>

        </div>


        <button
          className="primary-button"
          onClick={() => setShowForm(true)}
        >
          + Create Purchase
        </button>

      </div>


      {error && (

        <div className="dashboard-error">
          {error}
        </div>

      )}

      {showForm && (
        <PurchaseForm
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
        />
      )}

      <div className="products-card">

        <div className="table-wrapper">

          <table className="products-table">

            <thead>

              <tr>

                <th>
                  Purchase Number
                </th>

                <th>
                  Supplier
                </th>

                <th>
                  Total Amount
                </th>

                <th>
                  Status
                </th>

                <th>
                  Date
                </th>

                <th>
                  Actions
                </th>

              </tr>

            </thead>


            <tbody>

              {purchases.length === 0 ? (

                <tr>

                  <td
                    colSpan="6"
                    className="empty-state"
                  >
                    No purchases found.
                  </td>

                </tr>

              ) : (

                purchases.map(
                  (purchase) => (

                    <tr
                      key={purchase.id}
                    >

                      <td>

                        <strong>
                          {
                            purchase.purchase_number
                          }
                        </strong>

                      </td>


                      <td>
                        {suppliers.find(
                          (supplier) =>
                            supplier.id ===
                            purchase.supplier_id
                        )?.name || purchase.supplier_id}
                      </td>


                      <td>
                        {formatCurrency(
                          purchase.total_amount
                        )}
                      </td>


                      <td>

                        <span
                          className={getPurchaseStatusClass(
                            purchase.status
                          )}
                        >
                          {
                            purchase.status
                          }
                        </span>

                      </td>


                      <td>

                        {purchase.created_at
                          ? new Date(
                              purchase.created_at
                            ).toLocaleDateString()
                          : "N/A"}

                      </td>


                      <td>

                        {purchase.status ===
                        "PENDING" ? (

                          <button
                            className="edit-button"
                            onClick={() =>
                              handleReceive(
                                purchase.id
                              )
                            }
                          >
                            Receive
                          </button>

                        ) : (

                          <span>
                            Completed
                          </span>

                        )}

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


export default Purchases;