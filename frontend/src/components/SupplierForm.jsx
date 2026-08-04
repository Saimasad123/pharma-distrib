import { useEffect, useState } from "react";

function SupplierForm({
  supplier,
  onSubmit,
  onCancel,
}) {
  const [formData, setFormData] = useState({
    name: "",
    contact_person: "",
    phone: "",
    email: "",
    address: "",
    tax_number: "",
  });

  useEffect(() => {
    if (supplier) {
      setFormData({
        name: supplier.name || "",
        contact_person:
          supplier.contact_person || "",
        phone: supplier.phone || "",
        email: supplier.email || "",
        address: supplier.address || "",
        tax_number:
          supplier.tax_number || "",
      });
    }
  }, [supplier]);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    onSubmit(formData);
  };

  return (
    <div className="product-form-card">
      <div className="form-header">
        <h2>
          {supplier
            ? "Edit Supplier"
            : "Add New Supplier"}
        </h2>

        <button
          type="button"
          onClick={onCancel}
          className="close-button"
        >
          ×
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">

          {/* Supplier Name */}

          <div className="form-group">
            <label>Supplier Name</label>

            <input
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter supplier name"
              required
            />
          </div>

          {/* Contact Person */}

          <div className="form-group">
            <label>Contact Person</label>

            <input
              name="contact_person"
              value={
                formData.contact_person
              }
              onChange={handleChange}
              placeholder="Enter contact person"
            />
          </div>

          {/* Phone */}

          <div className="form-group">
            <label>Phone</label>

            <input
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="Enter phone number"
            />
          </div>

          {/* Email */}

          <div className="form-group">
            <label>Email</label>

            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter email address"
            />
          </div>

          {/* Tax Number */}

          <div className="form-group">
            <label>Tax Number</label>

            <input
              name="tax_number"
              value={
                formData.tax_number
              }
              onChange={handleChange}
              placeholder="Enter tax number"
            />
          </div>

          {/* Address */}

          <div className="form-group">
            <label>Address</label>

            <input
              name="address"
              value={formData.address}
              onChange={handleChange}
              placeholder="Enter supplier address"
            />
          </div>

        </div>

        <div className="form-actions">

          <button
            type="button"
            onClick={onCancel}
            className="secondary-button"
          >
            Cancel
          </button>

          <button
            type="submit"
            className="primary-button"
          >
            {supplier
              ? "Update Supplier"
              : "Create Supplier"}
          </button>

        </div>
      </form>
    </div>
  );
}

export default SupplierForm;