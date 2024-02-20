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
});
