function openSubMenu() {
    document.getElementById("floors").style.color = "red";
}

document.addEventListener("DOMContentLoaded", function() {
    var rows = document.querySelectorAll(".clickable-row");
    rows.forEach(function(row) {
        row.addEventListener("click", function() {
            window.location.href = row.dataset.href;
        });
    });
});

// Admin Floor

var button = document.getElementById("stack-dropdown-button");

button.addEventListener("click", function() {
    this.classList.add("clicked");
    this.classList.remove("not-hovered");
});
   
button.addEventListener("mouseleave", function() {
    this.classList.add("not-hovered");
    this.classList.remove("clicked");
});

function changeColor(button) {
    // Remove the 'active' class from all buttons
    var buttons = document.querySelectorAll('.btn-secondary');
    buttons.forEach(function(btn) {
      btn.classList.remove('active');
    });
  
    // Add the 'active' class to the clicked button
    button.classList.add('active');
  }

