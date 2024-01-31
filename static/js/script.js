// Responsive navbar
function myFunction() {
  var x = document.getElementById("myNavbar");
  if (x.className === "navbar") {
    x.className += " responsive";
  } else {
    x.className = "navbar";
  }
}

//Common
$(document).ready(function () {
  function fadeOutAlert() {
    $(".alert").fadeOut();
  }

  setTimeout(fadeOutAlert, 10000);

  $(".alert").click(function () {
    fadeOutAlert();
  });

  function animateProgressBar() {
    var progressBar = $(".progress-bar");
    progressBar.animate({ width: "0%" }, 10000, "linear");
  }

  animateProgressBar();
});

// Login / Signup Page
document.addEventListener("DOMContentLoaded", function () {
  const togglePasswords = document.querySelectorAll(".togglePassword");
  const passwords = document.querySelectorAll(".password");

  if (togglePasswords.length === passwords.length) {
    togglePasswords.forEach(function (togglePassword, index) {
      togglePassword.addEventListener("click", function (e) {
        const type =
          passwords[index].getAttribute("type") === "password"
            ? "text"
            : "password";
        passwords[index].setAttribute("type", type);
        togglePassword.classList.toggle("fa-eye");
        togglePassword.classList.toggle("fa-eye-slash");
      });
    });
  }
});

// Password validation module
document.addEventListener("DOMContentLoaded", function () {
  var password = document.getElementById("password"),
    confirm_password = document.getElementById("confirm_password");

  function validatePassword() {
    var passwordValue = password.value;
    var confirmPasswordValue = confirm_password.value;

    // Reset custom validity
    password.setCustomValidity("");
    confirm_password.setCustomValidity("");

    // Check if passwords match
    if (passwordValue !== confirmPasswordValue) {
      confirm_password.setCustomValidity("Passwords Don't Match");
    }

    // Check for strong password criteria
    var strongRegex =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!strongRegex.test(passwordValue)) {
      password.setCustomValidity(
        "Password must be at least 8 characters long and contain at least one lowercase letter, one uppercase letter, one number, and one special character (@$!%*?&)"
      );
    }
  }

  if (password && confirm_password) {
    password.addEventListener("input", validatePassword);
    confirm_password.addEventListener("input", validatePassword);
  }
});

// Date fields validation module
document.addEventListener("DOMContentLoaded", function () {
  var publicationMonth = document.getElementsByName("publication_month")[0],
    coverageTo = document.getElementsByName("coverage_to")[0];

  function validateDateFields() {
    var publicationMonthValue = new Date(publicationMonth.value);
    var coverageToValue = new Date(coverageTo.value);

    // Reset custom validity
    publicationMonth.setCustomValidity("");
    coverageTo.setCustomValidity("");

    // Check if publication_month is less than or equal to coverage_to
    if (publicationMonthValue > coverageToValue) {
      publicationMonth.setCustomValidity(
        "No Coverage! (Publication month should be less than or equal to Coverage to)"
      );
    }
  }

  if (publicationMonth && coverageTo) {
    publicationMonth.addEventListener("input", validateDateFields);
    coverageTo.addEventListener("input", validateDateFields);
  }
});

// Add smooth scrolling to all links
$("a").on("click", function (event) {
  // Make sure this.hash has a value before overriding default behavior
  if (this.hash !== "") {
    // Prevent default anchor click behavior
    event.preventDefault();

    // Store hash
    var hash = this.hash;

    // Using jQuery's animate() method to add smooth page scroll
    // The optional number (800) specifies the number of milliseconds it takes to scroll to the specified area
    $("html, body").animate(
      {
        scrollTop: $(hash).offset().top,
      },
      800,
      function () {
        // Add hash (#) to URL when done scrolling (default click behavior)
        window.location.hash = hash;
      }
    );
  } // End if
});
