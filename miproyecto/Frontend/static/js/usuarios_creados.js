document.addEventListener('DOMContentLoaded', function () {
  const token = getCookie('csrftoken');
  let usuarioSeleccionado = null;
  const estadoButton = document.getElementById('usuarios-btn-estado');
  const estadoSelect = document.getElementById('usuarios-accion-estado');
  const eliminarButton = document.getElementById('usuarios-btn-eliminar');
  const resetPasswordButton = document.getElementById('usuarios-btn-reset-password');
  const resetPasswordOverlay = document.getElementById('resetPasswordOverlay');
  const resetPasswordUsername = document.getElementById('resetPasswordUsername');
  const resetNewPassword = document.getElementById('resetNewPassword');
  const resetConfirmPassword = document.getElementById('resetConfirmPassword');
  const resetPasswordError = document.getElementById('resetPasswordError');
  const resetPasswordSubmit = document.getElementById('resetPasswordSubmit');
  const resetPasswordCancel = document.getElementById('resetPasswordCancel');

  const usuariosTableBody = document.querySelector('tbody');
  if (usuariosTableBody) usuariosTableBody.addEventListener('click', function (event) {
    const row = event.target.closest('tr[data-user-id]');
    if (!row || !usuariosTableBody.contains(row)) return;
    document.querySelectorAll('tr[data-user-id]').forEach(item => {
      item.classList.remove('registro-seleccionado');
      item.setAttribute('aria-selected', 'false');
    });
    row.classList.add('registro-seleccionado');
    row.setAttribute('aria-selected', 'true');
    usuarioSeleccionado = row;
    if (estadoButton) estadoButton.disabled = false;
    if (eliminarButton) eliminarButton.disabled = false;
    if (resetPasswordButton) resetPasswordButton.disabled = false;
    if (estadoSelect) estadoSelect.value = '';
  });

  if (estadoButton) estadoButton.addEventListener('click', function () {
    if (!usuarioSeleccionado) return alert('Selecciona un usuario antes de cambiar su estado.');
    const userId = usuarioSeleccionado.dataset.userId;
    const estadoActual = usuarioSeleccionado.querySelector('.usuario-activo')?.dataset.active === 'true';
    const accion = estadoSelect?.value;
    if (!accion) return alert('Selecciona si deseas activar o desactivar el usuario.');
    if ((accion === 'activar' && estadoActual) || (accion === 'desactivar' && !estadoActual)) {
      return alert(`El usuario ya está ${accion === 'activar' ? 'activo' : 'inactivo'}.`);
    }
    if (!confirm(`¿Estás seguro de que deseas ${accion} este usuario?`)) return;
    handleAction(userId, 'toggle_estado', usuarioSeleccionado);
  });

  if (eliminarButton) eliminarButton.addEventListener('click', function () {
    if (!usuarioSeleccionado) return alert('Selecciona un usuario antes de eliminarlo.');
    if (confirm('¿Estás seguro de que deseas eliminar este usuario? Esta acción no se puede deshacer.')) {
      handleAction(usuarioSeleccionado.dataset.userId, 'delete', usuarioSeleccionado);
    }
  });

  if (resetPasswordButton) resetPasswordButton.addEventListener('click', function () {
    if (!usuarioSeleccionado) return alert('Selecciona un usuario antes de restablecer su contraseña.');
    const role = usuarioSeleccionado.children[3]?.textContent.trim();
    const username = usuarioSeleccionado.children[0]?.textContent.trim();
    if (role !== 'Usuario') {
      return alert('Solo puedes restablecer contraseñas de usuarios con rol Usuario.');
    }

    resetPasswordUsername.textContent = `Usuario seleccionado: ${username}`;
    resetNewPassword.value = '';
    resetConfirmPassword.value = '';
    resetPasswordError.textContent = '';
    resetPasswordError.style.display = 'none';
    resetPasswordOverlay.hidden = false;
    resetNewPassword.focus();
  });

  if (resetPasswordCancel) resetPasswordCancel.addEventListener('click', function () {
    resetPasswordOverlay.hidden = true;
  });

  if (resetPasswordSubmit) resetPasswordSubmit.addEventListener('click', async function () {
    if (!usuarioSeleccionado) return;
    const newPassword = resetNewPassword.value;
    const confirmPassword = resetConfirmPassword.value;
    if (!newPassword || !confirmPassword) {
      showResetPasswordError('Completa y confirma la nueva contraseña.');
      return;
    }
    if (newPassword !== confirmPassword) {
      showResetPasswordError('Las contraseñas no coinciden.');
      return;
    }

    resetPasswordSubmit.disabled = true;
    try {
      const response = await fetch(`/accounts/api/usuarios/${usuarioSeleccionado.dataset.userId}/reset-password/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token,
        },
        body: JSON.stringify({
          new_password: newPassword,
          confirm_password: confirmPassword,
        }),
      });
      const body = await response.json();
      if (!response.ok || !body.success) {
        showResetPasswordError(body.error || 'No se pudo restablecer la contraseña.');
        return;
      }

      resetPasswordOverlay.hidden = true;
      alert(body.message);
    } catch (error) {
      console.error('Error al restablecer la contraseña:', error);
      showResetPasswordError('Error de conexión. Intenta de nuevo.');
    } finally {
      resetPasswordSubmit.disabled = false;
    }
  });

  function showResetPasswordError(message) {
    resetPasswordError.textContent = message;
    resetPasswordError.style.display = 'block';
  }

  function actualizarEstadoUsuario(row, activo) {
    const activoCell = row.querySelector('.usuario-activo');
    if (activoCell) {
      activoCell.dataset.active = String(activo);
      const icon = activoCell.querySelector('.estado-icono');
      const text = activoCell.querySelector('.estado-texto');
      if (icon) {
        icon.textContent = activo ? '✓' : '✕';
        icon.classList.toggle('estado-activo', activo);
        icon.classList.toggle('estado-inactivo', !activo);
      }
      if (text) text.textContent = activo ? 'Activado' : 'Bloqueado';
    }
    if (estadoButton) estadoButton.textContent = 'Cambiar estado';
    if (estadoSelect) estadoSelect.value = '';
  }

  function limpiarSeleccion() {
    usuarioSeleccionado = null;
    if (estadoButton) estadoButton.disabled = true;
    if (eliminarButton) eliminarButton.disabled = true;
    if (resetPasswordButton) resetPasswordButton.disabled = true;
  }

  function eliminarFila(row) {
    row.remove();
    limpiarSeleccion();
  }

  function actualizarAccion(action, row, body) {
    if (action === 'delete') {
      eliminarFila(row);
      return;
    }
    if (action === 'toggle_estado') {
      actualizarEstadoUsuario(row, body.activo);
    }
  }

  function handleAction(userId, action, row) {
    fetch(`/accounts/api/usuarios/${userId}/`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': token,
      },
      body: JSON.stringify({ action }),
    })
      .then(response => response.json().then(data => ({ status: response.status, body: data })))
      .then(({ status, body }) => {
        if (status >= 400 || !body.success) {
          alert(body.error || 'Ocurrió un error al procesar la acción.');
          return;
        }
        actualizarAccion(action, row, body);
      })
      .catch(error => {
        console.error('Error de red:', error);
        alert('Error de red. Intenta de nuevo.');
      });
  }
});
