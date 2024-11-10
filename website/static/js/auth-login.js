function togglePassword() {
    const passwordInput = document.getElementById("password");
    const eyeIcon = document.getElementById("eye-icon");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        eyeIcon.src = visibilityOnImg;
    } else {
        passwordInput.type = "password";
        eyeIcon.src = visibilityOffImg;
    }
}
