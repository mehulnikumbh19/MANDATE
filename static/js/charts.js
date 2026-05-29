/**
 * charts.js – Dark command-center charts for MANDATE.
 * Uses dark background, neon-style colors, and clean typography.
 */

function initDashboardCharts() {
  if (!window.MANDATE_STATS) return;

  const stats = window.MANDATE_STATS;

  // Set Chart.js global defaults for dark theme
  Chart.defaults.color = '#94a3b8';
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size = 11;

  const riskColors = {
    'Low':      '#10b981',
    'Medium':   '#06b6d4',
    'High':     '#f59e0b',
    'Critical': '#ef4444',
    'Unknown':  '#64748b'
  };

  const statusColors = {
    'Approved':                    '#10b981',
    'Approved with Exception':     '#f59e0b',
    'Rejected':                    '#ef4444',
    'Pending Approval':            '#3b82f6',
    'Draft':                       '#64748b',
    'Not Started':                 '#475569',
    'In Review':                   '#06b6d4',
    'Pending Evidence':            '#f59e0b',
    'Pending Vendor Response':     '#f59e0b',
    'Pending Risk Decision':       '#3b82f6',
    'Approved with Conditions':    '#f59e0b',
    'Reassessment Required':       '#ef4444'
  };

  // Risk doughnut
  const riskLabels = stats.riskLabels || [];
  const riskData = stats.riskData || [];
  const riskBg = riskLabels.map(l => riskColors[l] || '#475569');

  const riskCtx = document.getElementById('riskChart');
  if (riskCtx) {
    new Chart(riskCtx, {
      type: 'doughnut',
      data: {
        labels: riskLabels,
        datasets: [{
          data: riskData,
          backgroundColor: riskBg,
          borderWidth: 2,
          borderColor: '#131a28',
          hoverOffset: 8,
          hoverBorderColor: '#1e293b'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 10,
              padding: 14,
              usePointStyle: true,
              pointStyleWidth: 10,
              font: { family: 'Inter', size: 10, weight: '500' },
              color: '#94a3b8'
            }
          },
          tooltip: {
            backgroundColor: '#0f1520',
            borderColor: '#1e293b',
            borderWidth: 1,
            titleColor: '#e2e8f0',
            bodyColor: '#94a3b8',
            padding: 10,
            cornerRadius: 6,
            callbacks: {
              label: function(ctx) {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = total > 0 ? Math.round((ctx.raw / total) * 100) : 0;
                return ` ${ctx.label}: ${ctx.raw} (${pct}%)`;
              }
            }
          }
        },
        cutout: '68%'
      }
    });
  }

  // Status polar area
  const statusLabels = stats.statusLabels || [];
  const statusData = stats.statusData || [];
  const statusBg = statusLabels.map(l => statusColors[l] || '#3b82f6');

  const statusCtx = document.getElementById('statusChart');
  if (statusCtx) {
    new Chart(statusCtx, {
      type: 'polarArea',
      data: {
        labels: statusLabels,
        datasets: [{
          data: statusData,
          backgroundColor: statusBg.map(c => c + '99'),
          borderWidth: 1,
          borderColor: statusBg
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            ticks: { display: false },
            grid: { color: 'rgba(30, 41, 59, 0.6)', lineWidth: 1 },
            angleLines: { color: 'rgba(30, 41, 59, 0.4)' }
          }
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 10,
              padding: 14,
              usePointStyle: true,
              pointStyleWidth: 10,
              font: { family: 'Inter', size: 10, weight: '500' },
              color: '#94a3b8'
            }
          },
          tooltip: {
            backgroundColor: '#0f1520',
            borderColor: '#1e293b',
            borderWidth: 1,
            titleColor: '#e2e8f0',
            bodyColor: '#94a3b8',
            padding: 10,
            cornerRadius: 6
          }
        }
      }
    });
  }
}
