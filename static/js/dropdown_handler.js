$(document).ready(function() {
    $('#dropdown-word-cloud').change(function() {
        var selectedCompany = $(this).val();
        $.ajax({
            url: '/update-word-cloud',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'selectedCompany': selectedCompany }),
            success: function(response) {
                if (response && response.length > 0) {
                    var wordCloudElement = document.getElementById('word-cloud');
                    var width = wordCloudElement.offsetWidth;
                    var height = wordCloudElement.offsetHeight;

                    WordCloud(document.getElementById('word-cloud'), {
                        list: response, // Assuming response is like [['word', 5], ['hi', 10]]
                        gridSize: 10, // Increased from 8 to 10 for more space between words
                        weightFactor: function (size) {
                            // Adjusted calculation for font size scaling
                            const minFontSize = 10;
                            const maxFontSize = 60;
                    
                            // Determine the max count for scaling
                            const maxCount = Math.max(...response.map(item => item[1]));
                            const minCount = Math.min(...response.map(item => item[1]));
                    
                            // Scale size between minFontSize and maxFontSize more aggressively
                            const scaleFactor = (maxFontSize - minFontSize) / (maxCount - minCount);
                            return (size - minCount) * scaleFactor + minFontSize;
                        },
                        fontFamily: 'Roboto, sans-serif',
                        color: 'random-dark',
                        rotateRatio: 0,
                        backgroundColor: '#ffffff'
                    });
                    
                    
                } else {
                    console.log('No data returned for word cloud');
                }
            },
            error: function(error) {
                console.error("Error updating word cloud:", error);
            }
        });
    });
});
