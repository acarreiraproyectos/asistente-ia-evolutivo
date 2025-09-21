#!/bin/bash
# install.sh

echo "🔧 Instalando Asistente IA Evolutivo..."
echo "📦 Instalando dependencias..."

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-virtual-assistant.txt

# Crear estructura de directorios
mkdir -p assets/sprites assets/sounds config data logs models

echo "✅ Instalación completada!"
echo "🚀 Ejecuta: python main.py"