#!/bin/bash

# Script para corregir permisos de cámara en Docker
echo "🔧 Configurando permisos de cámara para Docker..."

# Verificar que las cámaras existan
if [ ! -e /dev/video0 ]; then
    echo "❌ /dev/video0 no encontrado"
    exit 1
fi

if [ ! -e /dev/video1 ]; then
    echo "❌ /dev/video1 no encontrado"
    exit 1
fi

# Cambiar permisos de las cámaras
echo "📷 Configurando permisos de /dev/video0 y /dev/video1..."
sudo chmod 666 /dev/video0
sudo chmod 666 /dev/video1

# Verificar permisos
echo "✅ Permisos configurados:"
ls -la /dev/video0
ls -la /dev/video1

echo "✅ Configuración de cámara completada"
