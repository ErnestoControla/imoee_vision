#!/bin/bash

# Script de gestión para IMoEE Vision Application

APP_DIR="/home/ernesto/Documentos/Proyectos/imoee_vision/asistente"
SERVICE_NAME="imoee-vision.service"

# Función para mostrar ayuda
show_help() {
    echo "🔧 Gestor de IMoEE Vision Application"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start     - Iniciar la aplicación"
    echo "  stop      - Detener la aplicación"
    echo "  restart   - Reiniciar la aplicación"
    echo "  status    - Ver estado de la aplicación"
    echo "  logs      - Ver logs de la aplicación"
    echo "  enable    - Habilitar inicio automático"
    echo "  disable   - Deshabilitar inicio automático"
    echo "  setup     - Configurar inicio automático"
    echo "  help      - Mostrar esta ayuda"
    echo ""
}

# Función para iniciar la aplicación
start_app() {
    echo "🚀 Iniciando IMoEE Vision Application..."
    cd "$APP_DIR"
    sudo systemctl start "$SERVICE_NAME"
    echo "✅ Aplicación iniciada"
}

# Función para detener la aplicación
stop_app() {
    echo "🛑 Deteniendo IMoEE Vision Application..."
    cd "$APP_DIR"
    sudo systemctl stop "$SERVICE_NAME"
    echo "✅ Aplicación detenida"
}

# Función para reiniciar la aplicación
restart_app() {
    echo "🔄 Reiniciando IMoEE Vision Application..."
    cd "$APP_DIR"
    sudo systemctl restart "$SERVICE_NAME"
    echo "✅ Aplicación reiniciada"
}

# Función para ver estado
status_app() {
    echo "📊 Estado de IMoEE Vision Application:"
    sudo systemctl status "$SERVICE_NAME"
}

# Función para ver logs
logs_app() {
    echo "📋 Logs de IMoEE Vision Application:"
    sudo journalctl -u "$SERVICE_NAME" -f
}

# Función para habilitar inicio automático
enable_app() {
    echo "✅ Habilitando inicio automático..."
    sudo systemctl enable "$SERVICE_NAME"
    echo "✅ Inicio automático habilitado"
}

# Función para deshabilitar inicio automático
disable_app() {
    echo "❌ Deshabilitando inicio automático..."
    sudo systemctl disable "$SERVICE_NAME"
    echo "✅ Inicio automático deshabilitado"
}

# Función para configurar inicio automático
setup_app() {
    echo "🔧 Configurando inicio automático..."
    cd "$APP_DIR"
    ./setup_autostart.sh
}

# Procesar argumentos
case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        status_app
        ;;
    logs)
        logs_app
        ;;
    enable)
        enable_app
        ;;
    disable)
        disable_app
        ;;
    setup)
        setup_app
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Comando no reconocido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
