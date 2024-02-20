function generateWordCloudForCompany(selectedCompany) {
    $.ajax({
        url: '/update-word-cloud',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 'selectedCompany': selectedCompany }), // Corrected the typo here
        success: function(response) {
            if (response && response.length > 0) {
                WordCloud(document.getElementById('word-cloud'), {
                    list: response,
                    gridSize: 10,
                    weightFactor: function (size) {
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
}


$(document).ready(function() {
    // Trigger word cloud generation for the initially selected company on load
    var initialSelectedCompany = $('#dropdown-word-cloud').val();
    generateWordCloudForCompany(initialSelectedCompany);

    // Also regenerate the word cloud whenever the dropdown selection changes
    $('#dropdown-word-cloud').change(function() {
        var selectedCompany = $(this).val();
        generateWordCloudForCompany(selectedCompany);
    });
});
