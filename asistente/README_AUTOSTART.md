# 🚀 Configuración de Inicio Automático - IMoEE Vision Application

## 📋 Descripción

Este documento describe cómo configurar el inicio automático de la aplicación IMoEE Vision cuando se reinicie el sistema.

## 🔧 Configuración Implementada

### ✅ Servicios Systemd Creados

1. **`imoee-vision.service`** - Servicio principal para inicio automático
2. **`imoee-vision-script.service`** - Versión alternativa con script personalizado

### 📁 Scripts de Gestión

1. **`setup_autostart.sh`** - Configura el inicio automático
2. **`start_application.sh`** - Script de inicio robusto
3. **`manage_application.sh`** - Gestor completo de la aplicación

## 🚀 Uso Rápido

### Configurar Inicio Automático
```bash
cd /home/ernesto/Documentos/Proyectos/imoee_vision/asistente
./setup_autostart.sh
```

### Gestión de la Aplicación
```bash
# Iniciar aplicación
./manage_application.sh start

# Detener aplicación
./manage_application.sh stop

# Reiniciar aplicación
./manage_application.sh restart

# Ver estado
./manage_application.sh status

# Ver logs en tiempo real
./manage_application.sh logs
```

## 📊 Comandos Systemd Directos

```bash
# Ver estado del servicio
sudo systemctl status imoee-vision.service

# Iniciar manualmente
sudo systemctl start imoee-vision.service

# Detener
sudo systemctl stop imoee-vision.service

# Reiniciar
sudo systemctl restart imoee-vision.service

# Ver logs
sudo journalctl -u imoee-vision.service -f

# Habilitar/deshabilitar inicio automático
sudo systemctl enable imoee-vision.service
sudo systemctl disable imoee-vision.service
```

## 🔄 Comportamiento al Reiniciar

1. **Al iniciar el sistema:**
   - Docker se inicia automáticamente
   - El servicio `imoee-vision.service` se ejecuta
   - Los contenedores se levantan automáticamente
   - La aplicación queda disponible

2. **Al apagar el sistema:**
   - Los contenedores se detienen correctamente
   - Docker se cierra de forma ordenada

## 🛠️ Solución de Problemas

### Si la aplicación no inicia automáticamente:

1. **Verificar que el servicio esté habilitado:**
   ```bash
   sudo systemctl is-enabled imoee-vision.service
   ```

2. **Ver logs del servicio:**
   ```bash
   sudo journalctl -u imoee-vision.service -f
   ```

3. **Reiniciar el servicio:**
   ```bash
   sudo systemctl restart imoee-vision.service
   ```

### Si Docker no está disponible:

1. **Verificar estado de Docker:**
   ```bash
   sudo systemctl status docker
   ```

2. **Iniciar Docker manualmente:**
   ```bash
   sudo systemctl start docker
   ```

## 📝 Archivos de Configuración

- **`/etc/systemd/system/imoee-vision.service`** - Servicio systemd
- **`/home/ernesto/Documentos/Proyectos/imoee_vision/asistente/`** - Directorio de la aplicación

## ✅ Estado Actual

- ✅ Servicio systemd creado y habilitado
- ✅ Inicio automático configurado
- ✅ Scripts de gestión disponibles
- ✅ Documentación completa

## 🎯 Próximos Pasos

1. Reiniciar el sistema para probar el inicio automático
2. Verificar que la aplicación se inicie correctamente
3. Usar los scripts de gestión para controlar la aplicación

---

**Nota:** La aplicación se iniciará automáticamente en el próximo reinicio del sistema.
