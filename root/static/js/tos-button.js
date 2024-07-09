const button = document.getElementById('tos-btn');
const bg = document.getElementById('tos-card-container-bg')
const container = document.getElementById('tos-card-container');
const card = document.getElementById('tos-card');
const head = document.getElementById('tos-head');
const content = document.getElementById('tos-content')

function showTOS() {
    bg.classList.remove('hidden');
    container.classList.remove('hidden');
    card.classList.remove('hidden');
    head.classList.remove('hidden');
    content.classList.remove('hidden');
}

function hideTOS() {
    bg.classList.add('hidden');
    container.classList.add('hidden')
    card.classList.add('hidden');
    head.classList.add('hidden');
    content.classList.add('hidden');
}

button.addEventListener('click', showTOS);
bg.addEventListener('click', hideTOS);