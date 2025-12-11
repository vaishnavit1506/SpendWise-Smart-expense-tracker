// General utility functions

// Format currency
function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2
  }).format(amount);
}

// Format percentage
function formatPercentage(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 0,
    maximumFractionDigits: 1
  }).format(value / 100);
}

// Confirm delete operations
document.addEventListener('DOMContentLoaded', function() {
  const deleteButtons = document.querySelectorAll('.btn-delete');
  deleteButtons.forEach(button => {
    button.addEventListener('click', function(event) {
      if (!confirm('Are you sure you want to delete this item?')) {
        event.preventDefault();
      }
    });
  });
});
