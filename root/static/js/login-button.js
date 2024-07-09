const loginBtn = document.getElementById('login-btn');
const loginForm = document.querySelector('.Login-content');

loginBtn.addEventListener('click', function(event) {
  event.preventDefault(); // Prevent the default form submission

  // Create fragments for the explosion effect
  for (let i = 0; i < 50; i++) {
    const fragment = document.createElement('div');
    fragment.classList.add('fragment');

    const x = loginBtn.offsetWidth / 2;
    const y = loginBtn.offsetHeight / 2;
    const angle = Math.random() * Math.PI * 2;
    const distance = Math.random() * 200;
    const dx = x + Math.cos(angle) * distance;
    const dy = y + Math.sin(angle) * distance;

    fragment.style.setProperty('--dx', `${dx - x}px`);
    fragment.style.setProperty('--dy', `${dy - y}px`);
    fragment.style.left = `${x}px`;
    fragment.style.top = `${y}px`;

    loginBtn.appendChild(fragment);
  }


  // Set a timeout for the duration of the animation (1 second)
  setTimeout(() => {
    loginForm.submit(); // Submit the form after the animation
  }, 500); // 1000ms = 1s, matches the duration of the animation
});