var pressed = false;
var loader = document.getElementById('loader');

// Handles the loading animation
document.getElementById('submit-button').addEventListener('click', function(event) {
    loader.style.display = "block";
});