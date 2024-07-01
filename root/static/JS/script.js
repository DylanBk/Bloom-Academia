// VARIABLES
email = document.getElementById('email');
password = document.getElementById('password');

// CECK
if (window.location.href.includes('createuser')) {
    error_message = document.getElementById('create-user-error-msg');
}
else if (window.location.href.includes('login')) {
    error_message = document.getElementById('login-error-msg');
}


function email_check(email) {
    const email_regex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    let check = email_regex.test(email);

    if (!check) {
        error_message.textContent = "Please enter a valid email.";
    }
    else {
        error_message.textContent = "";
    }
};

function password_check(password) {
    const password_regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    let check = password_regex.test(password);

    if (!check) {
        error_message.textContent = "Please enter a valid password.";
    }
    else {
        error_message.textContent = "";
    }
};