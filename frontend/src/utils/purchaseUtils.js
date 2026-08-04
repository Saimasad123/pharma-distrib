export const formatCurrency = (value) => {
  const safeValue = Number(value ?? 0);

  return `Rs. ${safeValue.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
};

export const getPurchaseStatusClass = (status) => {
  return status === 'RECEIVED'
    ? 'status-badge status-confirmed'
    : 'status-badge status-pending';
};
