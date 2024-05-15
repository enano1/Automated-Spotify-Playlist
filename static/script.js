// Handles the loading animation

// loader holds reference to Document Object Model (DOM) element with the ID 'loader'
var loader = document.getElementById('loader');
// Handler gets executed when event ("click") happens
document.getElementById('submit-button').addEventListener('click', function(event) {
    // loader.style.display = "block";
    fadeIn(loader);
});


// Function to fade in elements
function fadeIn(element) {
    let op = 0.1;  // initial opacity
    element.style.display = 'block';    // Ensure element is visible

    // Set interval (10 millisec) to gradually increase opacity
    let timer = setInterval(function () {
        // Check if fully opaque, stop interval
        if (op >= 1){
            clearInterval(timer);
        }
        element.style.opacity = op;
        element.style.filter = 'alpha(opacity=' + op * 100 + ")";   // For older versions of Internet Explorer
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

// as soon as the webpage has completely loaded, the element
// with the ID "fade" will begin to fade into view
window.onload = function() {
    let form = document.getElementById('fade');
    fadeIn(form);
};

