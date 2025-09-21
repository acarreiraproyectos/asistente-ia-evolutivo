#!/bin/bash
# verify_installation.sh

echo "🔍 Verificando instalación..."

# Verificar Python
if ! command -v python &> /dev/null; then
    echo "❌ Python no está instalado"
    exit 1
fi

# Verificar dependencias
if ! python -c "import pandas, numpy, requests" &> /dev/null; then
    echo "❌ Dependencias principales faltantes"
    exit 1
fi

# Verificar estructura de directorios
directories=("assets/sprites" "config" "data" "logs")
for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Directorio $dir no existe"
        exit 1
    fi
done

echo "✅ Todo verificado correctamente!"