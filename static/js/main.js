document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('is-open');
    });
  }

  var amountOptions = document.querySelectorAll('.amount-option');
  var amountInput = document.getElementById('monto');
  amountOptions.forEach(function (opt) {
    opt.addEventListener('click', function () {
      amountOptions.forEach(function (o) { o.classList.remove('is-selected'); });
      opt.classList.add('is-selected');
      if (amountInput) {
        amountInput.value = opt.getAttribute('data-amount');
      }
    });
  });

  var payMethods = document.querySelectorAll('.pay-method');
  payMethods.forEach(function (method) {
    method.addEventListener('click', function () {
      payMethods.forEach(function (m) { m.classList.remove('is-selected'); });
      method.classList.add('is-selected');
      var radio = method.querySelector('input[type="radio"]');
      if (radio) radio.checked = true;
    });
  });

  var modalEliminar = document.getElementById('modal-eliminar');
  var modalNombre = document.getElementById('modal-eliminar-nombre');
  var modalForm = document.getElementById('modal-eliminar-form');
  document.querySelectorAll('[data-eliminar-url]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (!modalEliminar || !modalForm) return;
      if (modalNombre) {
        modalNombre.textContent = btn.getAttribute('data-eliminar-nombre');
      }
      modalForm.setAttribute('action', btn.getAttribute('data-eliminar-url'));
      modalEliminar.classList.add('is-open');
    });
  });
  document.querySelectorAll('[data-modal-cerrar]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (modalEliminar) modalEliminar.classList.remove('is-open');
    });
  });
  if (modalEliminar) {
    modalEliminar.addEventListener('click', function (e) {
      if (e.target === modalEliminar) modalEliminar.classList.remove('is-open');
    });
  }

  var heroCard = document.querySelector('.viking-card');
  if (heroCard) {
    heroCard.style.opacity = '0';
    heroCard.style.transform = 'translateY(14px)';
    requestAnimationFrame(function () {
      heroCard.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      heroCard.style.opacity = '1';
      heroCard.style.transform = 'translateY(0)';
    });
  }
});
