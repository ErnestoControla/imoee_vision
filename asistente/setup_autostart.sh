#!/bin/bash

# Script para configurar el inicio automático de IMoEE Vision Application

echo "🔧 Configurando inicio automático de IMoEE Vision Application..."

# Verificar si el usuario tiene permisos de sudo
if ! sudo -n true 2>/dev/null; then
    echo "❌ Este script requiere permisos de sudo"
    exit 1
fi

# Copiar el servicio systemd
echo "📋 Copiando servicio systemd..."
sudo cp imoee-vision.service /etc/systemd/system/

# Recargar systemd
echo "🔄 Recargando systemd..."
sudo systemctl daemon-reload

# Habilitar el servicio
echo "✅ Habilitando servicio de inicio automático..."
sudo systemctl enable imoee-vision.service

# Verificar estado
echo "📊 Verificando estado del servicio..."
sudo systemctl is-enabled imoee-vision.service

echo ""
echo "🎉 Configuración completada!"
echo ""
echo "📝 Comandos útiles:"
echo "   • Ver estado: sudo systemctl status imoee-vision.service"
echo "   • Iniciar manualmente: sudo systemctl start imoee-vision.service"
echo "   • Detener: sudo systemctl stop imoee-vision.service"
echo "   • Ver logs: sudo journalctl -u imoee-vision.service -f"
echo ""
echo "🔄 La aplicación se iniciará automáticamente al reiniciar el sistema"
