function generateCountResponseBarChart() {
    // Read CSV file using fetch API
    fetch('data/twcs.csv')
        .then(response => response.text())
        .then(csvData => {
            // Parse CSV data
            const parsedData = Papa.parse(csvData, { header: true }).data;

            // Initialize company response count object
            const responseCounts = {};

            // Iterate through parsed data
            parsedData.forEach(row => {
                // Check if the tweet is inbound (sent by a customer to the company)
                if (row.inbound === 'False') {
                    // Extract company name from text column
                    const companyName = row.author_id

                    responseCounts[companyName] = (responseCounts[companyName] || 0) + 1;
                }
            });

            // Sort companies by response counts in descending order
            const sortedCompanies = Object.keys(responseCounts).sort((a, b) => responseCounts[b] - responseCounts[a]);

            // Take top 20 companies
            const top20Companies = sortedCompanies.slice(0, 20);

            // Extract company names and response counts for top 20 companies
            const companyNames = top20Companies;
            const responseRates = top20Companies.map(company => responseCounts[company]);

            // Generate bar chart
            const ctx = document.getElementById('responseRateChart').getContext('2d');
            const responseRateChart = new Chart(ctx, {
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
        });
}

// Add event listener for button click event
document.getElementById('generateChartButton').addEventListener('click', function() {
    document.getElementById('chartContainer').style.display = 'block'; // Show chart container
    generateCountResponseBarChart(); // Call function to generate chart
});

