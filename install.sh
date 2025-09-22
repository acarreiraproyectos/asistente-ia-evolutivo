#!/bin/bash
# install.sh - Script de instalación del Asistente IA Evolutivo

echo "🔧 Instalando Asistente IA Evolutivo..."
echo "========================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar Python
if ! command -v python &> /dev/null; then
    print_error "Python no está instalado"
    echo "Por favor instala Python 3.8+ desde https://python.org"
    exit 1
fi

# Verificar versión de Python
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    print_error "Se requiere Python 3.8 o superior. Versión actual: $PYTHON_VERSION"
    exit 1
fi

print_status "Python $PYTHON_VERSION detectado"

# Crear entorno virtual
echo "🐍 Creando entorno virtual..."
python -m venv venv

if [ $? -ne 0 ]; then
    print_error "Error creando entorno virtual"
    exit 1
fi

print_status "Entorno virtual creado"

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    print_error "Error activando entorno virtual"
    exit 1
fi

# Actualizar pip
echo "🔄 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📦 Instalando dependencias principales..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    print_error "Error instalando dependencias principales"
    exit 1
fi

echo "📦 Instalando dependencias del asistente virtual..."
pip install -r requirements-virtual-assistant.txt

if [ $? -ne 0 ]; then
    print_warning "Error instalando dependencias del asistente virtual (puede continuar)"
fi

# Crear estructura de directorios
echo "📁 Creando estructura de directorios..."
mkdir -p assets/sprites assets/sounds config data logs models tests examples scripts utils docs

# Crear archivos de configuración básicos
echo "⚙️  Creando configuraciones iniciales..."

# Crear .env desde ejemplo
if [ ! -f .env ]; then
    cp .env.example .env
    print_status "Archivo .env creado (edita con tus configuraciones)"
else
    print_warning "Archivo .env ya existe"
fi

# Crear technology_recommendations.json si no existe
if [ ! -f data/technology_recommendations.json ]; then
    python -c "
import json
from pathlib import Path

# Crear recomendaciones por defecto
default_recommendations = {
    'web_application': {
        'rapid_prototyping': [
            {
                'language': 'JavaScript',
                'framework': 'React',
                'suitability_score': 95,
                'pros': ['Alta demanda', 'Gran comunidad', 'Rápido desarrollo'],
                'cons': ['Configuración compleja', 'Curva de aprendizaje media'],
                'learning_curve': 'medium',
                'community_support': 'excellent',
                'performance': 'high',
                'cost': 'free'
            }
        ]
    }
}

# Guardar
Path('data').mkdir(exist_ok=True)
with open('data/technology_recommendations.json', 'w', encoding='utf-8') as f:
    json.dump(default_recommendations, f, indent=2, ensure_ascii=False)
    "
    print_status "Base de conocimientos de tecnologías creada"
fi

# Hacer los scripts ejecutables
chmod +x install.sh
chmod +x verify_installation.sh

print_status "Instalación completada exitosamente!"
echo ""
echo "🚀 Para iniciar el asistente:"
echo "   source venv/bin/activate    # Activar entorno virtual"
echo "   python main.py              # Ejecutar en modo interactivo"
echo "   python main.py --virtual    # Ejecutar con asistente virtual"
echo ""
echo "📖 Revisa docs/setup_guide.md para más información"