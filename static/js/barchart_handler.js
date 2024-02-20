// Global variable to hold the chart instance
let barChartInstance = null;

function generateCountResponseBarChart() {
    fetch('/get-bar-chart-data')
        .then(response => response.json())
        .then(data => {
            const { companyNames, responseRates } = data;
            const ctx = document.getElementById('responseRateChart').getContext('2d');

            // If there's an existing chart instance, destroy it before creating a new one
            if (barChartInstance) {
                barChartInstance.destroy();
            }

            // Create a new chart instance
            barChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: companyNames,
                    datasets: [{
                        label: 'Response Count',
                        data: responseRates,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });

            // Remove the loading message, if present
            const container = document.getElementById('barChartContainer');
            const pElement = container.querySelector('p');
            if (pElement) {
                pElement.remove();
            }
        })
        .catch(error => {
            console.error("Error loading bar chart data:", error);
        });
}

// Debounce function to limit how often a function is executed
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        }, wait);
        if (immediate && !timeout) func.apply(context, args);
    };
}

// Function to initialize or redraw the bar chart, ensuring container visibility
function initOrRedrawBarChart() {
    document.getElementById('barChartContainer').style.display = 'block';
    generateCountResponseBarChart();
}

// Event listener for DOMContentLoaded to trigger the initial chart generation
document.addEventListener('DOMContentLoaded', initOrRedrawBarChart);

// Redraw the bar chart upon window resize with debounce to improve performance
window.addEventListener('resize', debounce(initOrRedrawBarChart, 100));
