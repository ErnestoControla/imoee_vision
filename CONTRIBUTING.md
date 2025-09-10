# Guía de Contribución

¡Gracias por tu interés en contribuir a Imoee Vision! 🚀

## Cómo Contribuir

### 1. Fork y Clone
```bash
git clone https://github.com/tu-usuario/imoee_vision.git
cd imoee_vision
```

### 2. Configurar Entorno de Desarrollo
```bash
# Backend
cd asistente
pip install -r requirements/local.txt

# Frontend
cd frontend
npm install
```

### 3. Crear Rama
```bash
git checkout -b feature/nueva-funcionalidad
```

### 4. Hacer Cambios
- Sigue las convenciones de código existentes
- Agrega tests para nuevas funcionalidades
- Actualiza documentación si es necesario

### 5. Ejecutar Tests
```bash
# Backend
cd asistente
python manage.py test

# Frontend
cd frontend
npm test
```

### 6. Commit y Push
```bash
git add .
git commit -m "feat: agregar nueva funcionalidad"
git push origin feature/nueva-funcionalidad
```

### 7. Crear Pull Request
- Describe claramente los cambios
- Incluye screenshots si aplica
- Referencia issues relacionados

## Convenciones de Código

### Python (Backend)
- PEP 8
- Type hints cuando sea posible
- Docstrings para funciones públicas
- Tests unitarios obligatorios

### TypeScript (Frontend)
- ESLint configurado
- Prettier para formato
- Componentes funcionales con hooks
- Tests con Jest/React Testing Library

### Commits
Usa [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` nueva funcionalidad
- `fix:` corrección de bug
- `docs:` documentación
- `style:` formato, sin cambios de lógica
- `refactor:` refactorización
- `test:` agregar o modificar tests
- `chore:` tareas de mantenimiento

## Estructura del Proyecto

```
imoee_vision/
├── asistente/          # Backend Django
│   ├── analisis_coples/ # App principal
│   ├── compose/         # Docker configs
│   └── requirements/    # Dependencias Python
├── frontend/           # Frontend React
│   ├── src/
│   │   ├── components/ # Componentes reutilizables
│   │   ├── pages/      # Páginas
│   │   └── api/        # Servicios API
│   └── package.json
└── docs/              # Documentación
```

## Reportar Bugs

1. Verifica que no sea un bug conocido
2. Crea un issue con:
   - Descripción clara
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots si aplica
   - Información del sistema

## Solicitar Funcionalidades

1. Verifica que no esté en el roadmap
2. Crea un issue con:
   - Descripción detallada
   - Casos de uso
   - Beneficios esperados
   - Alternativas consideradas

## Preguntas

- GitHub Discussions para preguntas generales
- Issues para bugs y funcionalidades
- Email para temas privados

¡Gracias por contribuir! 🙏
