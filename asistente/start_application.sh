#!/bin/bash

# Script de inicio para IMoEE Vision Application
# Este script se ejecuta al iniciar el sistema

echo "🚀 Iniciando IMoEE Vision Application..."

# Cambiar al directorio de la aplicación
cd /home/ernesto/Documentos/Proyectos/imoee_vision/asistente

# Esperar a que Docker esté disponible
echo "⏳ Esperando a que Docker esté disponible..."
while ! docker info > /dev/null 2>&1; do
    echo "   Docker no está disponible, esperando..."
    sleep 5
done

echo "✅ Docker está disponible"

# Verificar si los contenedores ya están ejecutándose
if docker compose -f docker-compose.local.yml ps | grep -q "Up"; then
    echo "📦 Contenedores ya están ejecutándose"
else
    echo "🔄 Iniciando contenedores..."
    docker compose -f docker-compose.local.yml up -d
    
    # Esperar a que los servicios estén listos
    echo "⏳ Esperando a que los servicios estén listos..."
    sleep 10
    
    # Verificar estado de los contenedores
    echo "📊 Estado de los contenedores:"
    docker compose -f docker-compose.local.yml ps
fi

echo "✅ IMoEE Vision Application iniciada correctamente"
