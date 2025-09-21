function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const errorMsg = document.getElementById("error-message");

  // Dummy credentials
  const validUsername = "admin";
  const validPassword = "1234";

  if (username === validUsername && password === validPassword) {
    alert("✅ Login successful!");
    window.location.href = "dashbo.html"; // redirect
  } else {
    errorMsg.style.display = "block";
  }
}