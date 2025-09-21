# main.py
#!/usr/bin/env python3
"""
Punto de entrada principal del Asistente IA Evolutivo
"""
import sys
from pathlib import Path

# Añadir el directorio core al path
sys.path.append(str(Path(__file__).parent / "core"))

from core.assistant import AssistantCore
from core.virtual_assistant import VirtualAssistant
from core.software_dev_module import SoftwareDevModule

def main():
    """Función principal"""
    print("🚀 Iniciando Asistente IA Evolutivo...")
    
    try:
        # Inicializar el asistente principal
        assistant = AssistantCore()
        
        # Inicializar módulos adicionales
        dev_module = SoftwareDevModule()
        
        # Configurar integraciones
        assistant.setup_modules({
            'dev_module': dev_module,
            'virtual_assistant': None  # Se inicializa bajo demanda
        })
        
        # Verificar si se solicita el asistente virtual
        if len(sys.argv) > 1 and sys.argv[1] == "--virtual":
            virtual_assistant = VirtualAssistant()
            virtual_assistant.start()
        else:
            # Modo consola interactivo
            assistant.run_interactive_mode()
            
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()