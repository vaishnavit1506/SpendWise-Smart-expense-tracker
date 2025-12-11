// Chart.js configurations and settings

// Generate random colors with good contrast for charts
function generateChartColors(count) {
  const colors = [
    '#3498db', '#2ecc71', '#9b59b6', '#e74c3c', 
    '#f39c12', '#1abc9c', '#34495e', '#16a085',
    '#27ae60', '#2980b9', '#8e44ad', '#f1c40f'
  ];
  
  // If we need more colors than are predefined, generate them
  if (count > colors.length) {
    for (let i = colors.length; i < count; i++) {
      // Generate a random hex color
      const randomColor = '#' + Math.floor(Math.random()*16777215).toString(16);
      colors.push(randomColor);
    }
  }
  
  return colors.slice(0, count);
}

// Create a doughnut chart
function createDoughnutChart(ctx, labels, data) {
  const colors = generateChartColors(data.length);
  
  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            boxWidth: 12,
            padding: 15
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.raw || 0;
              const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
              const percentage = Math.round((value / total) * 100);
              return `${label}: ₹${value.toFixed(2)} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

// Create a bar chart
function createBarChart(ctx, labels, data, label) {
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: label,
        data: data,
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '₹' + value;
            }
          }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              return '₹' + context.raw.toFixed(2);
            }
          }
        }
      }
    }
  });
}
