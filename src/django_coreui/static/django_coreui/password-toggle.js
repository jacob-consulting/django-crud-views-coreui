// Show/hide password: a button with data-password-toggle="#<input id>" flips the input between password and text.
// A static file (not inline) so the sign-in page works under a strict Content-Security-Policy.
document.addEventListener("click", function (event) {
  const button = event.target.closest("[data-password-toggle]");
  if (!button) return;
  const input = document.querySelector(button.dataset.passwordToggle);
  if (!input) return;
  input.type = input.type === "password" ? "text" : "password";
  button.setAttribute("aria-pressed", String(input.type === "text"));
});
