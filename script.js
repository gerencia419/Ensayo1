const menuToggle = document.getElementById('menuToggle');
const menu = document.getElementById('menu');
const form = document.getElementById('leadForm');
const formMessage = document.getElementById('formMessage');
const year = document.getElementById('year');

year.textContent = new Date().getFullYear();

menuToggle?.addEventListener('click', () => {
  menu.classList.toggle('open');
});

form?.addEventListener('submit', (event) => {
  event.preventDefault();
  const data = new FormData(form);
  const name = data.get('name');
  formMessage.textContent = `Gracias, ${name}. El equipo comercial de SOMATEC te contactará en menos de 24 horas hábiles.`;
  form.reset();
});
