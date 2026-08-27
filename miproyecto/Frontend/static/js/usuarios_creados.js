document.addEventListener('DOMContentLoaded', function () {
  const token = getCookie('csrftoken');
  let usuarioSeleccionado = null;
  const estadoButton = document.getElementById('usuarios-btn-estado');
  const estadoSelect = document.getElementById('usuarios-accion-estado');
  const eliminarButton = document.getElementById('usuarios-btn-eliminar');

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
    if (estadoSelect) estadoSelect.value = '';
  });

  if (estadoButton) estadoButton.addEventListener('click', function () {
    if (!usuarioSeleccionado) return alert('Selecciona un usuario antes de cambiar su estado.');
    const userId = usuarioSeleccionado.dataset.userId;
    const estadoActual = usuarioSeleccionado.querySelector('.usuario-activo')?.textContent.trim();
    const accion = estadoSelect?.value;
    if (!accion) return alert('Selecciona si deseas activar o desactivar el usuario.');
    if ((accion === 'activar' && estadoActual === 'Sí') || (accion === 'desactivar' && estadoActual === 'No')) {
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

  function actualizarEstadoUsuario(row, activo) {
    const activoCell = row.querySelector('.usuario-activo');
    if (activoCell) activoCell.textContent = activo ? 'Sí' : 'No';
    if (estadoButton) estadoButton.textContent = 'Cambiar estado';
    if (estadoSelect) estadoSelect.value = '';
  }

  function limpiarSeleccion() {
    usuarioSeleccionado = null;
    if (estadoButton) estadoButton.disabled = true;
    if (eliminarButton) eliminarButton.disabled = true;
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
