const matrix = document.getElementById("matrix");
const ctx = matrix.getContext("2d");

// Set the canvas size to fullscreen
matrix.height = window.innerHeight;
matrix.width = window.innerWidth;

// Create an array of characters to use for the rain
const characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+[]{}|;':\",.<>?/\\-=`~".split("");
const font_size = 10;
const columns = matrix.width / font_size; // number of columns for the rain
const drops = []; // an array of drops - one per column

// Fill the drops[] array with drops from the top of the screen
for (let x = 0; x < columns; x++) {
drops[x] = 1;
}

// Main animation loop
function draw() {
// Clear the canvas
ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
ctx.fillRect(0, 0, matrix.width, matrix.height);

ctx.fillStyle = "#0F0"; // Green text
ctx.font = font_size + "px arial";

// Loop through the drops[] array and draw a character for each drop
for (let i = 0; i < drops.length; i++) {
let text = characters[Math.floor(Math.random() * characters.length)];
ctx.fillText(text, i * font_size, drops[i] * font_size);

// Reset the drop to the top when it reaches the bottom of the screen
if (drops[i] * font_size > matrix.height && Math.random() > 0.975) {
  drops[i] = 0;
}

// Increment the y position of each drop
drops[i]++;

}

// Call the draw() function again in a few milliseconds
setTimeout(draw, 33);
}

draw();

document.getElementById("facebook").addEventListener("click", function(event){
    event.preventDefault();
    window.open(this.href, "_blank");
});

document.getElementById("instagram").addEventListener("click", function(event){
    event.preventDefault();
    window.open(this.href, "_blank");
});


document.getElementById("envelope").addEventListener("click", function(event){
    event.preventDefault();
    window.open(this.href, "_blank");
});

document.getElementById("github").addEventListener("click", function(event){
    event.preventDefault();
    window.open(this.href, "_blank");
});



