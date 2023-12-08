// Handles the loading animation
var pressed = false;
var loader = document.getElementById('loader');
document.getElementById('submit-button').addEventListener('click', function(event) {
    // loader.style.display = "block";
    fadeIn(loader);
});

// Function to fade in elements
function fadeIn(element) {
    let op = 0.1;  // initial opacity
    element.style.display = 'block';
    let timer = setInterval(function () {
        if (op >= 1){
            clearInterval(timer);
        }
        element.style.opacity = op;
        element.style.filter = 'alpha(opacity=' + op * 100 + ")";
        op += op * 0.1;
    }, 10);
}

// Function to fade out elements
function fadeOut(element) {
    let op = 1;  // initial opacity
    let timer = setInterval(function () {
        if (op <= 0.1){
            clearInterval(timer);
            element.style.display = 'none';
        }
        element.style.opacity = op;
        element.style.filter = 'alpha(opacity=' + op * 100 + ")";
        op -= op * 0.1;
    }, 10);
}

window.onload = function() {
    let form = document.getElementById('fade');
    fadeIn(form);
};

