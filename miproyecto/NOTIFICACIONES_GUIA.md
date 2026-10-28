# Sistema de Notificaciones Personalizado

## Descripción

Se ha implementado un sistema de notificaciones completamente personalizado para tu aplicación, con colores que coinciden con la identidad visual del proyecto (verde agrícola #388e3c, #2e7d32).

## Características

### 1. **Notificaciones Toast**
Notificaciones flotantes pequeñas en la esquina superior derecha que desaparecen a los 5 segundos. Los mensajes de Django y las llamadas a `alert()` también se muestran como notificaciones en las páginas que cargan `notificaciones.js`.

### 2. **Validación de Formularios**
Sistema inteligente de validación con mensajes en tiempo real.

### 3. **Mensajes de Error/Éxito**
Estilos personalizados para todos los mensajes de validación.

### 4. **Confirmaciones Modales**
Diálogos de confirmación con diseño cohesivo.

---

## Uso en el Frontend (JavaScript)

### Instancia Global: `notifySystem`

Está disponible globalmente en todas las páginas que incluyan `notificaciones.js`.

### Métodos Principales

#### 1. Notificaciones Simples

```javascript
// Éxito
notifySystem.showSuccess('Usuario creado correctamente', 4000);

// Error
notifySystem.showError('No se pudo guardar los datos', 5000);

// Advertencia
notifySystem.showWarning('Este archivo ya existe', 5000);

// Información
notifySystem.showInfo('Operación completada', 3000);
```

**Parámetros:**
- `message` (string): Mensaje a mostrar
- `duration` (number, opcional): Duración en milisegundos (0 = sin auto-cierre)
- Los mensajes de error y advertencia se cierran automáticamente después de 5 segundos.

---

#### 2. Validación de Campos Individuales

```javascript
const input = document.getElementById('email');

// Validar email
const isValid = notifySystem.isValidEmail('test@example.com'); // true/false

// Validar teléfono
const isValidPhone = notifySystem.isValidPhone('+502 7123-4567'); // true/false

// Marcar campo con error
notifySystem.markFieldError(input, 'El email no es válido');

// Marcar campo con éxito
notifySystem.markFieldSuccess(input);

// Limpiar validación
notifySystem.clearFieldValidation(input);
```

---

#### 3. Validación Completa de Formularios

```javascript
const form = document.getElementById('myForm');

const rules = {
  username: [
    { required: true },
    { minLength: 3 },
    { maxLength: 20 }
  ],
  email: [
    { required: true },
    { email: true }
  ],
  password: [
    { required: true },
    { minLength: 8 }
  ],
  phone: [
    { phone: true }
  ]
};

const errors = notifySystem.validateForm(form, rules);

if (Object.keys(errors).length === 0) {
  // Formulario válido
  console.log('Formulario válido, enviar...');
} else {
  // Hay errores
  console.log('Errores:', errors);
}
```

**Reglas Disponibles:**
- `required`: Campo obligatorio
- `email`: Validar formato email
- `phone`: Validar formato teléfono
- `minLength`: Longitud mínima
- `maxLength`: Longitud máxima
- `pattern`: Expresión regular personalizada
- `customValidator`: Función personalizada

---

#### 4. Confirmación Modal

```javascript
notifySystem.showConfirmation(
  'Eliminar Usuario',
  '¿Estás seguro de que deseas eliminar este usuario? Esta acción no se puede deshacer.',
  function() {
    // Acción confirmar
    console.log('Usuario eliminado');
  },
  function() {
    // Acción cancelar
    console.log('Cancelado');
  }
);
```

---

## Uso en Templates (Django)

### 1. Incluir CSS y JS

```html
{% load static %}
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="{% static 'css/mensajes.css' %}" />
</head>
<body>
  <!-- Tu contenido -->
  
  <script src="{% static 'js/notificaciones.js' %}"></script>
</body>
</html>
```

### 2. Usar en JavaScript dentro del Template

```html
<script>
  document.addEventListener('DOMContentLoaded', function() {
    // Mostrar notificación de éxito
    notifySystem.showSuccess('Bienvenido', 3000);
  });
</script>
```

### 3. Convertir Mensajes de Django

```html
{% if messages %}
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      {% for message in messages %}
        const type = '{{ message.tags }}';
        const text = '{{ message }}';
        if (type.includes('success')) {
          notifySystem.showSuccess('✓ ' + text);
        } else if (type.includes('error')) {
          notifySystem.showError('✕ ' + text);
        } else if (type.includes('warning')) {
          notifySystem.showWarning('⚠ ' + text);
        } else {
          notifySystem.showInfo('ℹ ' + text);
        }
      {% endfor %}
    });
  </script>
{% endif %}
```

---

## Ejemplos Prácticos

### Ejemplo 1: Validar Formulario de Registro

```javascript
const registerForm = document.getElementById('registerForm');

registerForm.addEventListener('submit', function(e) {
  e.preventDefault();

  const rules = {
    username: [{ required: true }, { minLength: 3 }],
    email: [{ required: true }, { email: true }],
    password: [{ required: true }, { minLength: 8 }],
    confirmPassword: [{ required: true }]
  };

  const errors = notifySystem.validateForm(registerForm, rules);

  if (Object.keys(errors).length === 0) {
    notifySystem.showSuccess('✓ Formulario válido, enviando...', 2000);
    // Enviar formulario
    registerForm.submit();
  }
});
```

### Ejemplo 2: Llamada AJAX con Notificaciones

```javascript
fetch('/api/save-data/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'John' })
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    notifySystem.showSuccess('✓ Datos guardados correctamente', 3000);
  } else {
    notifySystem.showError('✕ ' + (data.error || 'Error al guardar'), 4000);
  }
})
.catch(err => {
  notifySystem.showError('✕ Error de conexión', 5000);
});
```

### Ejemplo 3: Validación con Regla Personalizada

```javascript
const rules = {
  username: [
    { required: true },
    {
      customValidator: (value, fieldLabel) => {
        if (value.includes(' ')) {
          return fieldLabel + ' no puede contener espacios';
        }
        return null; // No hay error
      }
    }
  ]
};

notifySystem.validateForm(form, rules);
```

---

## Colores Personalizados del Proyecto

Los siguientes colores están integrados en el sistema:

### Verde (Éxito)
- **Primary**: #2e7d32
- **Light**: #81c784
- **Background**: #e8f5e9
- **Border**: #4caf50

### Rojo (Error)
- **Primary**: #c62828
- **Light**: #e57373
- **Background**: #ffebee
- **Border**: #f44336

### Naranja (Advertencia)
- **Primary**: #f57c00
- **Light**: #ffb74d
- **Background**: #fff3e0
- **Border**: #ff9800

### Azul (Información)
- **Primary**: #1565c0
- **Light**: #64b5f6
- **Background**: #e3f2fd
- **Border**: #2196f3

---

## Responsive Design

El sistema está completamente optimizado para dispositivos móviles:

- Notificaciones se adaptan al ancho de la pantalla
- Modales son responsivos
- Campos de formulario tienen estilos móviles específicos

---

## Archivos Incluidos

1. **`css/mensajes.css`** - Estilos principales del sistema
2. **`js/notificaciones.js`** - Lógica JavaScript del sistema

---

## Migración de Código Antiguo

Si tienes código antiguo que usa `alert()` o `.innerHTML`, aquí hay ejemplos de cómo migrar:

### Antiguo:
```javascript
alert('Usuario creado');
errorDiv.innerHTML = 'Error: Campo requerido';
```

### Nuevo:
```javascript
notifySystem.showSuccess('Usuario creado');
notifySystem.showError('Error: Campo requerido');
```

---

## Notas Importantes

1. **Auto-cierre**: Las notificaciones se cierran automáticamente según el tiempo especificado
2. **Stacking**: Múltiples notificaciones se apilan verticalmente
3. **Mobile First**: El diseño prioriza experiencia móvil
4. **Accesible**: Todos los elementos son accesibles por teclado
5. **Sin dependencias**: No requiere librerías externas

---

## Soporte Técnico

Para personalizar colores, edita las variables CSS en `css/mensajes.css`:

```css
:root {
  --color-success: #2e7d32;
  --color-error: #c62828;
  --color-warning: #f57c00;
  --color-info: #1565c0;
}
```
