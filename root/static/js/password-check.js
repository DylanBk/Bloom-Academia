// // --- VARIABLES ---

// let password = document.getElementById('signup-password');
// let error_message = document.getElementById('create-user-error-msg');
// let button = document.getElementById('signup-btn');
// let form = document.getElementById('signup-form');


// // --- PASSWORD CHECK ---

// function password_check(password) {
//     const password_regex = /^(?=.*[A-Z])(?=.*[@$!%*?&]).{8,}$/;
//     let check = password_regex.test(password);

//     if (!check) {
//         error_message.textContent = "Please enter a valid password.";
//         return false;
//     } else {
//         error_message.textContent = "";
//         return true;
//     }
// }

// function validateForm(event) {
//     const isPasswordValid = password_check(password.value);

//     if (!isPasswordValid) {
//         // Prevent form submission
//         event.preventDefault();
//     }
// }

// // Attach the validateForm function to the form's submit event
// if (form) {
//     form.addEventListener('submit', validateForm);
// }