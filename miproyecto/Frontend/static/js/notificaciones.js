/**
 * Sistema de notificaciones y validaciones personalizado
 * Colores del proyecto: Verde #388e3c, #2e7d32
 */

class NotificationSystem {
  constructor() {
    this.messages = {
      required_field: 'Este campo es obligatorio',
      invalid_email: 'Por favor ingresa un email válido',
      invalid_phone: 'Por favor ingresa un teléfono válido',
      min_length: 'Este campo requiere al menos {n} caracteres',
      max_length: 'Este campo no puede exceder {n} caracteres',
      password_mismatch: 'Las contraseñas no coinciden',
      field_duplicate: 'Este valor ya existe',
      network_error: 'Error de conexión, por favor intenta de nuevo',
      server_error: 'Error del servidor, por favor intenta más tarde',
      operation_success: 'Operación realizada correctamente',
      operation_failed: 'La operación no se pudo completar',
    };
  }

  /**
   * Mostrar notificación de éxito
   */
  showSuccess(message, duration = 2000) {
    this.showNotification(message, 'success', duration);
  }

  /**
   * Mostrar notificación de error
   */
  showError(message, duration = 2000) {
    this.showNotification(message, 'error', duration);
  }

  /**
   * Mostrar notificación de advertencia
   */
  showWarning(message, duration = 2000) {
    this.showNotification(message, 'warning', duration);
  }

  /**
   * Mostrar notificación de información
   */
  showInfo(message, duration = 2000) {
    this.showNotification(message, 'info', duration);
  }

  showAlert(message, duration = 2000) {
    const text = String(message);
    const type = /error|no se pudo|no se puede|fall[oó]|incorrect|inv[aá]lid/i.test(text)
      ? 'error'
      : /debes|selecciona|requerid|obligatori|falta/i.test(text)
        ? 'warning'
        : /correctamente|guardad[oa]|actualizad[oa]|eliminad[oa]/i.test(text)
          ? 'success'
          : 'info';

    this.showNotification(text, type, duration);
  }

  /**
   * Método principal para mostrar notificaciones
   */
  showNotification(message, type = 'info', duration = 2000) {
    // Buscar o crear contenedor de notificaciones
    let container = document.getElementById('notifications-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'notifications-container';
      container.style.cssText = `
        position: fixed;
        inset: 0;
        z-index: 10000;
        pointer-events: none;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 10px;
        padding: 20px;
        box-sizing: border-box;
      `;
      container.setAttribute('aria-live', 'polite');
      document.body.appendChild(container);
    }

    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.setAttribute('role', type === 'error' ? 'alert' : 'status');
    const content = document.createElement('div');
    content.className = 'notification-content';
    const icon = document.createElement('span');
    icon.className = 'notification-icon';
    icon.textContent = this.getIcon(type);
    const messageElement = document.createElement('span');
    messageElement.className = 'notification-message';
    messageElement.textContent = String(message);
    const closeButton = document.createElement('button');
    closeButton.className = 'notification-close';
    closeButton.setAttribute('aria-label', 'Cerrar');
    closeButton.type = 'button';
    closeButton.textContent = '×';
    content.append(icon, messageElement, closeButton);
    notification.appendChild(content);

    container.appendChild(notification);

    // Estilos específicos por tipo
    const styles = {
      success: {
        bg: '#e8f5e9',
        border: '#2e7d32',
        color: '#1b5e20',
      },
      error: {
        bg: '#ffebee',
        border: '#c62828',
        color: '#b71c1c',
      },
      warning: {
        bg: '#fff3e0',
        border: '#f57c00',
        color: '#e65100',
      },
      info: {
        bg: '#e3f2fd',
        border: '#1565c0',
        color: '#1565c0',
      },
    };

    const style = styles[type] || styles.info;
    notification.style.cssText = `
      background: ${style.bg};
      border-left: 4px solid ${style.border};
      color: ${style.color};
      padding: 14px 16px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 0.95rem;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      pointer-events: all;
      animation: notificationPopIn 0.25s ease-out;
      width: min(420px, 100%);
      box-sizing: border-box;
    `;

    // Cerrar notificación
    const closeBtn = closeButton;
    closeBtn.style.cssText = `
      background: none;
      border: none;
      color: ${style.color};
      font-size: 1.5rem;
      cursor: pointer;
      padding: 0;
      margin-left: auto;
      opacity: 0.7;
      transition: opacity 0.2s;
    `;
    closeBtn.onmouseover = () => closeBtn.style.opacity = '1';
    closeBtn.onmouseout = () => closeBtn.style.opacity = '0.7';
    closeBtn.onclick = () => this.closeNotification(notification);

    // Auto-cerrar después de duración
    if (duration !== 0) {
      setTimeout(() => this.closeNotification(notification), 2000);
    }
  }

  showPageMessages() {
    document.querySelectorAll('.messages-container, .messages').forEach(container => {
      const messages = container.querySelectorAll('.alert, .alert-operacion');
      if (messages.length) {
        messages.forEach(message => {
          const typeClass = Array.from(message.classList)
            .find(className => /^alert-(error|danger|warning|success|info)$/.test(className));
          const taggedType = typeClass ? typeClass.replace('alert-', '') : 'info';
          const type = taggedType === 'danger' ? 'error' : taggedType;
          this.showNotification(message.textContent.trim(), type, 2000);
        });
      } else if (container.textContent.trim()) {
        this.showNotification(container.textContent.trim(), 'info', 2000);
      }
      container.remove();
    });

    const messageSelectors = [
      ['#warningPopup .warning-text', 'warning'],
      ['#loginWarningPopup', 'error'],
      ['.success-banner', 'success'],
      ['.error-banner', 'error'],
      ['.lookup-message', 'warning'],
      ['.recovery-message', 'success'],
    ];
    messageSelectors.forEach(([selector, type]) => {
      document.querySelectorAll(selector).forEach(message => {
        const text = message.textContent.trim();
        if (text) this.showNotification(text, type, 2000);
        message.remove();
      });
    });
    document.getElementById('warningPopup')?.remove();
  }

  /**
   * Cerrar una notificación específica
   */
  closeNotification(notification) {
    notification.style.animation = 'notificationPopOut 0.2s ease-in forwards';
    setTimeout(() => notification.remove(), 300);
  }

  /**
   * Obtener icono según el tipo
   */
  getIcon(type) {
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ',
    };
    return icons[type] || '';
  }

  /**
   * Validar un formulario completo
   */
  validateForm(formElement, rules = {}) {
    const errors = {};
    const formData = new FormData(formElement);

    for (const [fieldName, fieldRules] of Object.entries(rules)) {
      const input = formElement.querySelector(`[name="${fieldName}"]`);
      if (!input) continue;

      const value = input.value.trim();
      const fieldLabel = input.getAttribute('data-label') || fieldName;

      for (const rule of fieldRules) {
        const error = this.validateField(value, rule, fieldLabel);
        if (error) {
          errors[fieldName] = error;
          this.markFieldError(input, error);
          break;
        } else {
          this.markFieldSuccess(input);
        }
      }
    }

    return errors;
  }

  /**
   * Validar un campo individual
   */
  validateField(value, rule, fieldLabel = 'Campo') {
    if (rule.required && !value) {
      return `${fieldLabel} es obligatorio`;
    }

    if (rule.email && value && !this.isValidEmail(value)) {
      return 'Por favor ingresa un email válido';
    }

    if (rule.phone && value && !this.isValidPhone(value)) {
      return 'Por favor ingresa un teléfono válido';
    }

    if (rule.minLength && value && value.length < rule.minLength) {
      return `${fieldLabel} requiere al menos ${rule.minLength} caracteres`;
    }

    if (rule.maxLength && value && value.length > rule.maxLength) {
      return `${fieldLabel} no puede exceder ${rule.maxLength} caracteres`;
    }

    if (rule.pattern && value && !rule.pattern.test(value)) {
      return rule.patternMessage || `${fieldLabel} tiene un formato inválido`;
    }

    if (rule.customValidator) {
      return rule.customValidator(value, fieldLabel);
    }

    return null;
  }

  /**
   * Marcar campo con error
   */
  markFieldError(input, message) {
    input.classList.add('field-error');
    input.classList.remove('field-success');
    input.style.borderColor = '#c62828';
    input.style.backgroundColor = 'rgba(255, 235, 238, 0.3)';

    // Remover mensaje anterior
    const oldMessage = input.parentElement.querySelector('.field-error-text');
    if (oldMessage) oldMessage.remove();

    // Añadir nuevo mensaje
    const errorText = document.createElement('small');
    errorText.className = 'field-error-text';
    errorText.textContent = message;
    errorText.style.cssText = `
      color: #c62828;
      font-size: 0.85rem;
      display: block;
      margin-top: 0.25rem;
    `;
    input.parentElement.appendChild(errorText);
  }

  /**
   * Marcar campo con éxito
   */
  markFieldSuccess(input) {
    input.classList.remove('field-error');
    input.classList.add('field-success');
    input.style.borderColor = '#2e7d32';
    input.style.backgroundColor = 'rgba(232, 245, 233, 0.3)';

    // Remover mensaje de error anterior
    const oldMessage = input.parentElement.querySelector('.field-error-text');
    if (oldMessage) oldMessage.remove();
  }

  /**
   * Limpiar validación de un campo
   */
  clearFieldValidation(input) {
    input.classList.remove('field-error', 'field-success');
    input.style.borderColor = '';
    input.style.backgroundColor = '';
    const errorText = input.parentElement.querySelector('.field-error-text');
    if (errorText) errorText.remove();
  }

  /**
   * Validaciones auxiliares
   */
  isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  isValidPhone(phone) {
    const re = /^[\d\s\-\+\(\)]+$/;
    return re.test(phone) && phone.replace(/\D/g, '').length >= 7;
  }

  /**
   * Mostrar modal de confirmación personalizado
   */
  showConfirmation(title, message, onConfirm, onCancel) {
    let modal = document.getElementById('confirmation-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'confirmation-modal';
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div class="confirmation-overlay"></div>
      <div class="confirmation-box">
        <h3>${title}</h3>
        <p>${message}</p>
        <div class="confirmation-buttons">
          <button class="btn-cancel" data-action="cancel">Cancelar</button>
          <button class="btn-confirm" data-action="confirm">Confirmar</button>
        </div>
      </div>
    `;

    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 10001;
      display: flex;
      align-items: center;
      justify-content: center;
    `;

    const overlay = modal.querySelector('.confirmation-overlay');
    overlay.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      z-index: 1;
    `;

    const box = modal.querySelector('.confirmation-box');
    box.style.cssText = `
      position: relative;
      z-index: 2;
      background: white;
      border-radius: 12px;
      padding: 24px;
      max-width: 400px;
      width: 90%;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
      border-top: 4px solid #2e7d32;
    `;

    const h3 = box.querySelector('h3');
    h3.style.cssText = 'margin: 0 0 12px; color: #1b5e20; font-size: 1.2rem;';

    const p = box.querySelector('p');
    p.style.cssText = 'margin: 8px 0; color: #555; font-size: 0.95rem;';

    const buttonsDiv = box.querySelector('.confirmation-buttons');
    buttonsDiv.style.cssText = `
      margin-top: 20px;
      display: flex;
      gap: 10px;
      justify-content: flex-end;
    `;

    const buttons = buttonsDiv.querySelectorAll('button');
    buttons.forEach(btn => {
      btn.style.cssText = `
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.95rem;
        font-weight: 600;
        transition: all 0.2s;
      `;
    });

    const confirmBtn = modal.querySelector('.btn-confirm');
    confirmBtn.style.cssText += `
      background: #2e7d32;
      color: white;
    `;
    confirmBtn.onmouseover = () => confirmBtn.style.background = '#1b5e20';
    confirmBtn.onmouseout = () => confirmBtn.style.background = '#2e7d32';

    const cancelBtn = modal.querySelector('.btn-cancel');
    cancelBtn.style.cssText += `
      background: #f0f0f0;
      color: #333;
    `;
    cancelBtn.onmouseover = () => cancelBtn.style.background = '#e0e0e0';
    cancelBtn.onmouseout = () => cancelBtn.style.background = '#f0f0f0';

    modal.onclick = (e) => {
      if (e.target === overlay) {
        this.closeConfirmation();
        if (onCancel) onCancel();
      }
    };

    confirmBtn.onclick = () => {
      this.closeConfirmation();
      if (onConfirm) onConfirm();
    };

    cancelBtn.onclick = () => {
      this.closeConfirmation();
      if (onCancel) onCancel();
    };

    modal.style.display = 'flex';
  }

  /**
   * Cerrar modal de confirmación
   */
  closeConfirmation() {
    const modal = document.getElementById('confirmation-modal');
    if (modal) {
      modal.style.display = 'none';
    }
  }
}

// Crear instancia global
const notifySystem = new NotificationSystem();
window.alert = message => notifySystem.showAlert(message);

// Agregar estilos necesarios al DOM si no existen
function initializeNotificationStyles() {
  if (!document.getElementById('notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
      @keyframes slideInRight {
        from {
          opacity: 0;
          transform: translateX(20px);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }

      @keyframes slideOutRight {
        to {
          opacity: 0;
          transform: translateX(20px);
        }
      }

      @keyframes notificationPopIn {
        from {
          opacity: 0;
          transform: scale(0.94);
        }
        to {
          opacity: 1;
          transform: scale(1);
        }
      }

      @keyframes notificationPopOut {
        to {
          opacity: 0;
          transform: scale(0.94);
        }
      }

      .notification {
        animation: slideInRight 0.3s ease-out;
      }

      .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .notification-icon {
        font-weight: bold;
        font-size: 1.1rem;
      }

      .notification-message {
        flex: 1;
      }

      .notification-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        margin-left: auto;
        opacity: 0.7;
        transition: opacity 0.2s;
        color: inherit;
      }

      .notification-close:hover {
        opacity: 1;
      }

      .field-error {
        border-color: #c62828 !important;
      }

      .field-success {
        border-color: #2e7d32 !important;
      }

      .field-error-text {
        color: #c62828;
        font-size: 0.85rem;
        display: block;
        margin-top: 0.25rem;
      }

      @media (max-width: 768px) {
        #notifications-container {
          padding: 16px !important;
        }
      }
    `;
    document.head.appendChild(style);
  }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initializeNotificationStyles();
    notifySystem.showPageMessages();
  });
} else {
  initializeNotificationStyles();
  notifySystem.showPageMessages();
}
