function generateCountResponseBarChart() {
    fetch('/get-bar-chart-data')
        .then(response => response.json())
        .then(data => {
            // Extract company names and response rates from the response
            const { companyNames, responseRates } = data;

            // Generate bar chart
            const ctx = document.getElementById('responseRateChart').getContext('2d');
            new Chart(ctx, {
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

            // Optionally, remove the loading message
            const container = document.getElementById('barChartContainer');
            const pElement = container.querySelector('p'); // Adjust the selector as needed
            if (pElement) {
                pElement.remove();
            }
        });
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('barChartContainer').style.display = 'block'; // Show chart container
    generateCountResponseBarChart(); // Call function to generate chart
});
