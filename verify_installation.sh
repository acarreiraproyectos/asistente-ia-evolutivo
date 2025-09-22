#!/bin/bash
# verify_installations.sh

echo "🔍 Verificando instalación del Asistente Virtual..."

# Verificar Python
if ! command -v python &> /dev/null; then
    echo "❌ Python no está instalado"
    exit 1
fi

# Verificar version de Python (3.11+)
PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$PYTHON_VERSION < 3.11" | bc -l) -eq 1 ]]; then
    echo "❌ Se requiere Python 3.11 o superior. Versión actual: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION instalado"

# Verificar dependencias principales
echo "Verificando dependencias principales..."
REQUIRED_PACKAGES=("pandas" "numpy" "requests" "fastapi" "uvicorn" "sqlalchemy" "openai")
for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python -c "import $package" &> /dev/null; then
        echo "❌ Paquete $package no está instalado"
        exit 1
    fi
done

# Verificar dependencias del asistente virtual
echo "Verificando dependencias del asistente virtual..."
AI_PACKAGES=("speech_recognition" "pyttsx3" "google.generativeai" "elevenlabs")
for package in "${AI_PACKAGES[@]}"; do
    if ! python -c "import $package" &> /dev/null; then
        echo "❌ Paquete de IA $package no está instalado"
        exit 1
    fi
done

# Verificar estructura de directorios
echo "Verificando estructura de directorios..."
DIRECTORIES=("app" "app/api" "app/core" "app/models" "app/services" "app/utils" "tests")
for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Directorio $dir no existe"
        exit 1
    fi
done

# Verificar archivos de configuración esenciales
echo "Verificando archivos de configuración..."
CONFIG_FILES=("requirements.txt" "requirements-virtual-assistant.txt" ".env.example" "Dockerfile")
for file in "${CONFIG_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Archivo $file no existe"
        exit 1
    fi
done

# Verificar servicios externos (Docker)
echo "Verificando servicios de apoyo..."
if command -v docker &> /dev/null; then
    if docker ps &> /dev/null; then
        echo "✅ Docker está ejecutándose"
        
        # Verificar contenedores esenciales
        if docker-compose ps | grep -q "postgres"; then
            echo "✅ PostgreSQL container está activo"
        else
            echo "⚠️  PostgreSQL container no está activo"
        fi
        
        if docker-compose ps | grep -q "redis"; then
            echo "✅ Redis container está activo"
        else
            echo "⚠️  Redis container no está activo"
        fi
    else
        echo "⚠️  Docker instalado pero no ejecutándose"
    fi
else
    echo "⚠️  Docker no instalado (algunas funciones estarán limitadas)"
fi

# Verificar variables de entorno
if [ -f ".env" ]; then
    echo "✅ Archivo .env encontrado"
    
    # Verificar variables críticas
    if grep -q "OPENAI_API_KEY" .env && ! grep -q "OPENAI_API_KEY=your-openai-api-key-here" .env; then
        echo "✅ OPENAI_API_KEY configurada"
    else
        echo "⚠️  OPENAI_API_KEY no configurada o usando valor por defecto"
    fi
    
    if grep -q "DATABASE_URL" .env && ! grep -q "DATABASE_URL=postgresql://user:password@localhost" .env; then
        echo "✅ DATABASE_URL configurada"
    else
        echo "⚠️  DATABASE_URL no configurada o usando valor por defecto"
    fi
else
    echo "❌ Archivo .env no encontrado. Copie .env.example a .env y configure las variables"
    exit 1
fi

echo "✅ Todo verificado correctamente!"
echo ""
echo "🎉 El asistente virtual está listo para usar!"
echo "📝 Ejecute 'make dev' para iniciar el servidor de desarrollo"
echo "📚 Consulte README.md para más instrucciones"