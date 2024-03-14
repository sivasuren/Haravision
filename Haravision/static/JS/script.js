// script.js
function previewImage(input) {
    const preview = document.getElementById('previewImg');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function detectDisease() {
    $.ajax({
        type: 'POST',
        url: '/upload',
        data: new FormData($('form')[0]),
        processData: false,
        contentType: false,
        success: function (data) {
            // Handle the response from the server and update the results on the page
            console.log('Response from server:', data);
            if (data.results) {
                // Loop through each result and update the page
                data.results.forEach(function(result, index) {
                    // Update the image element with the uploaded image
                    $('#previewImg' + (index+1)).attr('src', result.image_path);
                    // Update the result details
                    $('#diseasePrediction' + (index+1)).text('Predicted Disease: ' + result.disease_prediction);
                    $('#severity' + (index+1)).text('Disease Severity: ' + result.severity + '%');
                    if (result.solution) {
                        $('#solution' + (index+1)).text('Recommended Solution: ' + result.solution);
                    }
                    // Update the PI and PDI
                    $('#pi' + (index+1)).text('Percentage of Disease Incidence (PI): ' + ((result.infected_count / result.total_count) * 100).toFixed(2) + '%');
                    $('#pdi' + (index+1)).text('Percentage of Disease Index (PDI): ' + ((result.sum_ratings / (9 * result.total_count)) * 100).toFixed(2) + '%');
                });
                // Show the result container
                $('.image-preview').show();
                $('.result-details').show();
            }
        },
        error: function (error) {
            console.error('Error:', error);
        }
    });
}
