const form = document.getElementById("registerForm");

function togglePassword(id) {
  const input = document.getElementById(id);
  input.type = input.type === "password" ? "text" : "password";
}

form.addEventListener("submit", function(e) {
  e.preventDefault();

  let valid = true;

  // Name check
  const name = document.getElementById("name").value.trim();
  if (name === "") {
    document.getElementById("nameError").style.display = "block";
    valid = false;
  } else {
    document.getElementById("nameError").style.display = "none";
  }

  // Email check
  const email = document.getElementById("email").value.trim();
  const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;
  if (!email.match(emailPattern)) {
    document.getElementById("emailError").style.display = "block";
    valid = false;
  } else {
    document.getElementById("emailError").style.display = "none";
  }

  // Password check
  const password = document.getElementById("password").value.trim();
  if (password.length < 6) {
    document.getElementById("passwordError").style.display = "block";
    valid = false;
  } else {
    document.getElementById("passwordError").style.display = "none";
  }

  // Confirm Password check
  const confirmPassword = document.getElementById("confirmPassword").value.trim();
  if (password !== confirmPassword || confirmPassword === "") {
    document.getElementById("confirmError").style.display = "block";
    valid = false;
  } else {
    document.getElementById("confirmError").style.display = "none";
  }

  if (valid) {
    document.getElementById("successMsg").style.display = "block";
    setTimeout(() => {
      document.getElementById("successMsg").style.display = "none";
      form.reset();
    }, 2000);
  }
});