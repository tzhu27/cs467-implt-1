// Function to generate the word cloud for a selected company
function generateWordCloudForCompany(selectedCompany) {
    $.ajax({
        url: '/update-word-cloud',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 'selectedCompany': selectedCompany }),
        success: function(response) {
            if (response && response.length > 0) {
                WordCloud(document.getElementById('word-cloud-container'), {
                    list: response,
                    gridSize: 10,
                    weightFactor: function(size) {
                        const minFontSize = 10;
                        const maxFontSize = 60;
                        const maxCount = Math.max(...response.map(item => item[1]));
                        const minCount = Math.min(...response.map(item => item[1]));
                        const scaleFactor = (maxFontSize - minFontSize) / (maxCount - minCount);
                        return (size - minCount) * scaleFactor + minFontSize;
                    },
                    fontFamily: 'Roboto, sans-serif',
                    color: 'random-dark',
                    rotateRatio: 0,
                    backgroundColor: '#ffffff',
                    drawOutOfBound: false
                });
            } else {
                console.log('No data returned for word cloud');
            }
        },
        error: function(error) {
            console.error("Error updating word cloud:", error);
        }
    });
}
var myChart = null;

function sentimentAnalysisExec(selectedCompany) {
    $.ajax({
        url: '/update-sentiment-analysis',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 'selectedCompany': selectedCompany }),
        success: function(response) {
            if (response && response.Company) {
                // Create a horizontal bar chart using Chart.js
                var ctx = document.getElementById('combined-chart').getContext('2d');
                if (myChart) {
                    myChart.destroy();
                }
                if (window.wordPieChart) {
                    window.wordPieChart.destroy();
                }
                myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['Positive Words', 'Negative Words'],
                        datasets: [{
                            label: 'Sentiment Analysis for ' + response.Company,
                            data: [response.PositiveWords, response.NegativeWords],
                            backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(255, 99, 132, 0.6)'],
                            borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            xAxes: [{
                                ticks: {
                                    beginAtZero: true
                                }
                            }]
                        }
                    }
                });

                /*document.getElementById("sentiment-chart").onclick = function(event, elements) {

                    if (elements && elements.length > 0) {
                        var index = elements[0]._index;
                        if (index === 0) {
                            displayWords(response.Pos);
                        } else if (index === 1) {
                            displayWords(response.Neg);
                        }
                    }
                }*/
                // Attach click event handler to the chart
                ctx.canvas.onclick = function(event) {
                    var activePoint = myChart.getActiveElements(event)[0];
                    if (activePoint) {
                        var datasetIndex = activePoint.datasetIndex;
                        var index = activePoint.index;
                        if (datasetIndex === 0 && index === 0) {
                            displayWords(myChart, response.Pos);
                        } else if (datasetIndex === 0 && index === 1) {
                            displayWords(myChart, response.Neg);
                        }
                    }
                };

            } else {
                console.log('No data returned for Sentiment analysis');
            }
        },
        error: function(error) {
            console.error("Error updating SA:", error);
        }
    });
}

/*function displayWords(words) {
    // Assuming words is an object where keys are the words and values are their counts
    for (const word in words) {
        console.log(`${word}: ${words[word]}`);
    }
}*/
function displayWords(myChart, words) {
    // Extract words and counts from the object
    const labels = Object.keys(words);
    const data = Object.values(words);

    // Generate random colors for each word
    const colors = labels.map(() => '#' + Math.floor(Math.random() * 16777215).toString(16));

    // Create pie chart data
    const pieChartData = {
        labels: labels,
        datasets: [{
            data: data,
            backgroundColor: colors
        }]
    };

    // Get the canvas context
    const ctx = document.getElementById('combined-chart').getContext('2d');

    // Destroy previous chart if exists
    if (window.wordPieChart) {
        window.wordPieChart.destroy();
    }
    if (myChart) myChart.destroy();
    // Create new pie chart
    window.wordPieChart = new Chart(ctx, {
        type: 'pie',
        data: pieChartData,
        options: {
            responsive: true,
            legend: {
                position: 'bottom'
            },
            title: {
                display: true,
                text: 'Word Frequency'
            }
        }
    });
}

// Debounce function to limit how often a function is executed
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this,
            args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        }, wait);
        if (immediate && !timeout) func.apply(context, args);
    };
}

$(document).ready(function() {
    // Generate the word cloud for the initially selected company
    var initialSelectedCompany = $('#dropdown-word-cloud').val();
    generateWordCloudForCompany(initialSelectedCompany);

    // Handle dropdown selection change
    $('#dropdown-word-cloud').change(function() {
        var selectedCompany = $(this).val();
        generateWordCloudForCompany(selectedCompany);
    });

    // Redraw the word cloud upon window resize with debounce to improve performance
    var redrawDebounced = debounce(function() {
        generateWordCloudForCompany($('#dropdown-word-cloud').val());
    }, 100);

    window.addEventListener('resize', redrawDebounced);

    //SA
    var initialSelectedCompany = $('#sentiment-analysis').val();
    sentimentAnalysisExec(initialSelectedCompany);
    $('#sentiment-analysis').change(function() {
        var selectedCompany = $(this).val();
        sentimentAnalysisExec(selectedCompany);
    });
});