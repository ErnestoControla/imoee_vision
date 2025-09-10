# Imoee Vision - Sistema de Análisis de Coples

Sistema de análisis de coples utilizando visión por computadora y modelos de inteligencia artificial.

## 🚀 Características

- **Análisis en tiempo real** de coples mediante cámara webcam
- **Clasificación automática** usando modelos ONNX
- **Interfaz web moderna** con React y Material-UI
- **API REST completa** con Django
- **Base de datos PostgreSQL** para almacenamiento
- **Docker** para despliegue fácil

## 🏗️ Arquitectura

### Backend
- **Django** con Django REST Framework
- **PostgreSQL** como base de datos
- **OpenCV** para procesamiento de imágenes
- **ONNX Runtime** para inferencia de modelos
- **Docker** para containerización

### Frontend
- **React** con TypeScript
- **Material-UI** para componentes
- **Vite** como bundler
- **Axios** para comunicación con API

## 📦 Instalación

### Prerrequisitos
- Docker y Docker Compose
- Node.js 18+ (para desarrollo frontend)
- Python 3.9+ (para desarrollo backend)

### Desarrollo Local

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/imoee_vision.git
cd imoee_vision
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Iniciar servicios con Docker:**
```bash
docker-compose -f docker-compose.local.yml up -d
```

4. **Para desarrollo frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Base de datos
POSTGRES_DB=imoee_vision
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password

# Django
SECRET_KEY=tu_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# API
API_BASE_URL=http://localhost:8000/api
```

### Modelos ONNX

Los modelos de IA deben colocarse en:
```
asistente/analisis_coples/Modelos/
```

## 🚀 Uso

1. **Acceder a la aplicación:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - Admin Django: http://localhost:8000/admin

2. **Realizar análisis:**
   - Conectar cámara webcam
   - Hacer clic en "INICIAR ANÁLISIS"
   - Ver resultados en tiempo real

## 📊 API Endpoints

### Análisis
- `GET /api/analisis/resultados/recientes/` - Obtener análisis recientes
- `POST /api/analisis/realizar/` - Realizar nuevo análisis
- `GET /api/analisis/sistema/estado/` - Estado del sistema

### Imágenes
- `GET /api/analisis/imagenes/procesada/{id}/` - Imagen procesada
- `GET /api/analisis/imagenes/miniatura/{id}/` - Miniatura

## 🧪 Testing

```bash
# Backend
cd asistente
python manage.py test

# Frontend
cd frontend
npm test
```

## 📝 Desarrollo

### Estructura del Proyecto

```
imoee_vision/
├── asistente/                 # Backend Django
│   ├── analisis_coples/      # App principal
│   ├── compose/              # Configuraciones Docker
│   └── manage.py
├── frontend/                 # Frontend React
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── pages/           # Páginas
│   │   └── api/             # Servicios API
│   └── package.json
└── docker-compose.local.yml  # Docker para desarrollo
```

### Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🤝 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

## 📈 Roadmap

- [ ] Integración con cámaras GigE
- [ ] Análisis de detección de defectos
- [ ] Segmentación de piezas
- [ ] Dashboard de estadísticas
- [ ] API de exportación de datos
