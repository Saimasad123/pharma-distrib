import { useEffect, useState } from "react";

import { getSuppliers } from "../api/supplier";
import { getProducts } from "../api/product";


function PurchaseForm({ onSubmit, onCancel }) {
  const [suppliers, setSuppliers] = useState([]);
  const [products, setProducts] = useState([]);

  const [supplierId, setSupplierId] = useState("");
  const [purchaseNumber, setPurchaseNumber] = useState("");
  const [notes, setNotes] = useState("");

  const [items, setItems] = useState([
    {
      product_id: "",
      quantity: 1,
      unit_cost: "",
    },
  ]);

  const [loading, setLoading] = useState(true);


  // =====================================================
  // LOAD SUPPLIERS AND PRODUCTS
  // =====================================================

  useEffect(() => {
    const loadData = async () => {
      try {
        const [
          suppliersData,
          productsData,
        ] = await Promise.all([
          getSuppliers(),
          getProducts(),
        ]);

        setSuppliers(suppliersData);
        setProducts(productsData);

      } catch (err) {
        console.error(err);

        alert(
          err.response?.data?.detail ||
          "Failed to load suppliers or products."
        );

      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);


  // =====================================================
  // ADD ITEM
  // =====================================================

  const addItem = () => {
    setItems([
      ...items,
      {
        product_id: "",
        quantity: 1,
        unit_cost: "",
      },
    ]);
  };


  // =====================================================
  // REMOVE ITEM
  // =====================================================

  const removeItem = (index) => {

    if (items.length === 1) {
      return;
    }

    setItems(
      items.filter(
        (_, itemIndex) =>
          itemIndex !== index
      )
    );
  };


  // =====================================================
  // UPDATE ITEM
  // =====================================================

  const updateItem = (
    index,
    field,
    value
  ) => {

    const updatedItems = [
      ...items,
    ];

    updatedItems[index] = {
      ...updatedItems[index],
      [field]: value,
    };

    setItems(updatedItems);
  };


  // =====================================================
  // CALCULATE TOTAL
  // =====================================================

  const totalAmount = items.reduce(
    (total, item) => {

      const quantity =
        Number(item.quantity) || 0;

      const unitCost =
        Number(item.unit_cost) || 0;

      return (
        total +
        quantity * unitCost
      );

    },
    0
  );


  // =====================================================
  // SUBMIT
  // =====================================================

  const handleSubmit = async (event) => {

    event.preventDefault();


    if (!supplierId) {
      alert("Please select a supplier.");
      return;
    }


    if (!purchaseNumber.trim()) {
      alert(
        "Please enter a purchase number."
      );
      return;
    }


    for (const item of items) {

      if (!item.product_id) {
        alert(
          "Please select a product for every item."
        );
        return;
      }


      if (
        Number(item.quantity) <= 0
      ) {
        alert(
          "Quantity must be greater than zero."
        );
        return;
      }


      if (
        Number(item.unit_cost) < 0 ||
        item.unit_cost === ""
      ) {
        alert(
          "Unit cost cannot be negative or empty."
        );
        return;
      }

    }


    const purchaseData = {

      supplier_id:
        supplierId,

      purchase_number:
        purchaseNumber.trim(),

      notes:
        notes.trim() || null,

      items:
        items.map((item) => ({

          product_id:
            item.product_id,

          quantity:
            Number(item.quantity),

          unit_cost:
            Number(item.unit_cost),

        })),

    };


    await onSubmit(
      purchaseData
    );

  };


  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {

    return (
      <div className="form-card">

        <p>
          Loading suppliers and products...
        </p>

      </div>
    );

  }


  // =====================================================
  // FORM
  // =====================================================

  return (

    <div className="form-card">

      <div className="form-header">

        <div>

          <h2>
            Create Purchase
          </h2>

          <p>
            Add products purchased
            from a supplier.
          </p>

        </div>

      </div>


      <form
        onSubmit={handleSubmit}
      >

        {/* SUPPLIER */}

        <div className="form-group">

          <label>
            Supplier
          </label>

          <select
            value={supplierId}
            onChange={(event) =>
              setSupplierId(
                event.target.value
              )
            }
            required
          >

            <option value="">
              Select Supplier
            </option>

            {suppliers
              .filter(
                (supplier) =>
                  supplier.is_active !== false
              )
              .map((supplier) => (

                <option
                  key={supplier.id}
                  value={supplier.id}
                >
                  {supplier.name}
                </option>

              ))}

          </select>

        </div>


        {/* PURCHASE NUMBER */}

        <div className="form-group">

          <label>
            Purchase Number
          </label>

          <input
            type="text"
            placeholder="e.g. PO-0001"
            value={purchaseNumber}
            onChange={(event) =>
              setPurchaseNumber(
                event.target.value
              )
            }
            required
          />

        </div>


        {/* ITEMS */}

        <div className="purchase-items-section">

          <div className="section-header">

            <h3>
              Purchase Items
            </h3>

            <button
              type="button"
              className="primary-button"
              onClick={addItem}
            >
              + Add Product
            </button>

          </div>


          {items.map(
            (item, index) => (

              <div
                className="purchase-item-row"
                key={index}
              >

                {/* PRODUCT */}

                <div className="form-group">

                  <label>
                    Product
                  </label>

                  <select
                    value={
                      item.product_id
                    }
                    onChange={(
                      event
                    ) =>
                      updateItem(
                        index,
                        "product_id",
                        event.target.value
                      )
                    }
                    required
                  >

                    <option value="">
                      Select Product
                    </option>

                    {products
                      .filter(
                        (product) =>
                          product.is_active !== false
                      )
                      .map(
                        (product) => (

                          <option
                            key={
                              product.id
                            }
                            value={
                              product.id
                            }
                          >
                            {
                              product.name
                            }
                          </option>

                        )
                      )}

                  </select>

                </div>


                {/* QUANTITY */}

                <div className="form-group">

                  <label>
                    Quantity
                  </label>

                  <input
                    type="number"
                    min="1"
                    value={
                      item.quantity
                    }
                    onChange={(
                      event
                    ) =>
                      updateItem(
                        index,
                        "quantity",
                        event.target.value
                      )
                    }
                    required
                  />

                </div>


                {/* UNIT COST */}

                <div className="form-group">

                  <label>
                    Unit Cost
                  </label>

                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="0.00"
                    value={
                      item.unit_cost
                    }
                    onChange={(
                      event
                    ) =>
                      updateItem(
                        index,
                        "unit_cost",
                        event.target.value
                      )
                    }
                    required
                  />

                </div>


                {/* TOTAL */}

                <div className="form-group">

                  <label>
                    Total
                  </label>

                  <input
                    type="text"
                    value={(
                      Number(
                        item.quantity
                      ) *
                      Number(
                        item.unit_cost
                      )
                    ).toFixed(2)}
                    readOnly
                  />

                </div>


                {/* REMOVE */}

                <button
                  type="button"
                  className="delete-button"
                  onClick={() =>
                    removeItem(index)
                  }
                  disabled={
                    items.length === 1
                  }
                >
                  Remove
                </button>

              </div>

            )
          )}

        </div>


        {/* NOTES */}

        <div className="form-group">

          <label>
            Notes
          </label>

          <textarea
            rows="3"
            placeholder="Optional notes..."
            value={notes}
            onChange={(event) =>
              setNotes(
                event.target.value
              )
            }
          />

        </div>


        {/* TOTAL */}

        <div className="purchase-total">

          <strong>
            Total Purchase Amount:
          </strong>

          <span>
            Rs.{" "}
            {totalAmount.toLocaleString(
              undefined,
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }
            )}
          </span>

        </div>


        {/* ACTIONS */}

        <div className="form-actions">

          <button
            type="button"
            className="secondary-button"
            onClick={onCancel}
          >
            Cancel
          </button>


          <button
            type="submit"
            className="primary-button"
          >
            Create Purchase
          </button>

        </div>

      </form>

    </div>

  );
}


export default PurchaseForm;