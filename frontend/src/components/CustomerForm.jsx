import { useEffect, useState } from "react";

function CustomerForm({
  customer,
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
    if (customer) {
      setFormData({
        name: customer.name || "",
        contact_person:
          customer.contact_person || "",
        phone: customer.phone || "",
        email: customer.email || "",
        address: customer.address || "",
        tax_number:
          customer.tax_number || "",
      });
    }
  }, [customer]);

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
          {customer
            ? "Edit Customer"
            : "Add New Customer"}
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
          <div className="form-group">
            <label>Customer Name</label>

            <input
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter customer name"
              required
            />
          </div>

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

          <div className="form-group">
            <label>Phone</label>

            <input
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="Enter phone number"
            />
          </div>

          <div className="form-group">
            <label>Email</label>

            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter email"
            />
          </div>

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
        </div>

        <div className="form-group">
          <label>Address</label>

          <textarea
            name="address"
            value={formData.address}
            onChange={handleChange}
            placeholder="Enter customer address"
            rows="4"
          />
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
            {customer
              ? "Update Customer"
              : "Create Customer"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default CustomerForm;