let top20BarRTInstance = null;

function getTop20RTBarChart() {
    const ctx = document.getElementById('responseTimeChart').getContext('2d');
    fetch('/get-top20-comp-response-time')
        .then(response => response.json())
        .then(data => {
            // Extract company names and convert response times from seconds to hours
            data = JSON.parse(data)
            const companies = Object.keys(data);
            const responseTimesInHours = companies.map(company => (data[company].mean_response_time / 3600).toFixed(2));

            // Destroy the previous instance of the chart, if it exists
            if (top20BarRTInstance) {
                top20BarRTInstance.destroy();
            }

            // Create a new chart instance
            top20BarRTInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: companies,
                    datasets: [{
                        label: 'Avg Response Time',
                        data: responseTimesInHours,
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
            const container = document.getElementById('barChartTop20RTContainer');
            const pElement = container.querySelector('p');
            if (pElement) {
                pElement.remove();
            }
        })
        .catch(error => {
            console.error('Error loading the data: ', error);
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
    document.getElementById('barChartTop20RTContainer').style.display = 'block';
    getTop20RTBarChart();
}

// Event listener for DOMContentLoaded to trigger the initial chart generation
document.addEventListener('DOMContentLoaded', initOrRedrawBarChart);

// Redraw the bar chart upon window resize with debounce to improve performance
window.addEventListener('resize', debounce(initOrRedrawBarChart, 100));