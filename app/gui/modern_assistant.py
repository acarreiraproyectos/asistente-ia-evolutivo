import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from PIL import Image, ImageTk
import pygame
from app.services.voice_service import VoiceService
from app.services.ai.openai_service import OpenAIService

class ModernAssistant:
    def __init__(self):
        # Inicializar pygame para audio
        pygame.mixer.init()
        
        # Configuración de la ventana principal
        self.root = tk.Tk()
        self.root.title("Asistente Virtual IA")
        self.root.geometry("400x600")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(True, True)
        
        # Hacer ventana siempre visible
        self.root.attributes('-topmost', True)
        
        # Estado del asistente
        self.is_listening = False
        self.is_processing = False
        self.is_speaking = False
        
        # Servicios
        self.voice_service = VoiceService()
        self.ai_service = OpenAIService()
        
        # Configurar interfaz
        self.setup_ui()
        
        # Iniciar bucle de estado
        self.update_status_loop()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header con logo y título
        self.setup_header(main_frame)
        
        # Panel de estado
        self.setup_status_panel(main_frame)
        
        # Área de conversación
        self.setup_conversation_area(main_frame)
        
        # Panel de control
        self.setup_control_panel(main_frame)
        
        # Panel de configuración
        self.setup_settings_panel(main_frame)
        
        # Configurar estilos
        self.setup_styles()
    
    def setup_header(self, parent):
        """Configurar el encabezado"""
        header_frame = ttk.Frame(parent, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo (puedes reemplazar con una imagen)
        logo_label = ttk.Label(header_frame, text="🤖", font=('Arial', 24),
                              style='Dark.TLabel')
        logo_label.pack(side=tk.LEFT)
        
        # Título
        title_label = ttk.Label(header_frame, text="Asistente Virtual IA",
                               font=('Arial', 16, 'bold'), style='Dark.TLabel')
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Botón de cerrar
        close_btn = ttk.Button(header_frame, text="×", width=3,
                              command=self.root.quit, style='Close.TButton')
        close_btn.pack(side=tk.RIGHT)
    
    def setup_status_panel(self, parent):
        """Configurar panel de estado"""
        status_frame = ttk.Frame(parent, style='Status.TFrame')
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Indicador de estado
        self.status_indicator = tk.Canvas(status_frame, width=20, height=20,
                                         bg='#333333', highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        # Texto de estado
        self.status_label = ttk.Label(status_frame, text="Listo",
                                     style='Dark.TLabel')
        self.status_label.pack(side=tk.LEFT)
        
        # Indicador de actividad de audio
        self.audio_visualizer = tk.Canvas(status_frame, width=100, height=20,
                                         bg='#333333', highlightthickness=0)
        self.audio_visualizer.pack(side=tk.RIGHT)
    
    def setup_conversation_area(self, parent):
        """Configurar área de conversación"""
        conv_frame = ttk.Frame(parent, style='Dark.TFrame')
        conv_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Área de chat
        self.chat_area = scrolledtext.ScrolledText(
            conv_frame, wrap=tk.WORD, width=40, height=15,
            bg='#2d2d2d', fg='#ffffff', insertbackground='white',
            font=('Arial', 10), state=tk.DISABLED
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para diferentes tipos de mensajes
        self.chat_area.tag_config('user', foreground='#4fc3f7')
        self.chat_area.tag_config('assistant', foreground='#81c784')
        self.chat_area.tag_config('system', foreground='#ffb74d')
        self.chat_area.tag_config('error', foreground='#e57373')
    
    def setup_control_panel(self, parent):
        """Configurar panel de control"""
        control_frame = ttk.Frame(parent, style='Dark.TFrame')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón de micrófono principal
        self.mic_button = ttk.Button(
            control_frame, text="🎤 Iniciar Escucha", 
            command=self.toggle_listening, style='Primary.TButton'
        )
        self.mic_button.pack(fill=tk.X, pady=2)
        
        # Botones secundarios
        secondary_frame = ttk.Frame(control_frame, style='Dark.TFrame')
        secondary_frame.pack(fill=tk.X)
        
        ttk.Button(secondary_frame, text="📝 Texto", 
                  command=self.open_text_input).pack(side=tk.LEFT, expand=True)
        ttk.Button(secondary_frame, text="⚙️ Config", 
                  command=self.open_settings).pack(side=tk.LEFT, expand=True)
        ttk.Button(secondary_frame, text="🧹 Limpiar", 
                  command=self.clear_chat).pack(side=tk.LEFT, expand=True)
    
    def setup_settings_panel(self, parent):
        """Configurar panel de configuración (inicialmente oculto)"""
        self.settings_frame = ttk.Frame(parent, style='Dark.TFrame')
        
        # Configuraciones de voz
        ttk.Label(self.settings_frame, text="Voz:", style='Dark.TLabel').pack(anchor=tk.W)
        self.voice_var = tk.StringVar(value="español-latino")
        ttk.Combobox(self.settings_frame, textvariable=self.voice_var,
                    values=["español-latino", "español-espana", "inglés"]).pack(fill=tk.X)
        
        # Velocidad de habla
        ttk.Label(self.settings_frame, text="Velocidad:", style='Dark.TLabel').pack(anchor=tk.W)
        self.speed_var = tk.DoubleVar(value=1.0)
        ttk.Scale(self.settings_frame, from_=0.5, to=2.0, variable=self.speed_var,
                 orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # Ocultar inicialmente
        self.settings_visible = False
    
    def setup_styles(self):
        """Configurar estilos visuales"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores para modo oscuro
        style.configure('Dark.TFrame', background='#1a1a1a')
        style.configure('Dark.TLabel', background='#1a1a1a', foreground='white')
        style.configure('Status.TFrame', background='#2d2d2d')
        
        # Botones
        style.configure('Primary.TButton', background='#2196f3', foreground='white')
        style.map('Primary.TButton', 
                 background=[('active', '#1976d2'), ('pressed', '#0d47a1')])
        
        style.configure('Close.TButton', background='#f44336', foreground='white')
    
    def update_status_loop(self):
        """Bucle para actualizar el estado visual"""
        self.update_status_indicator()
        self.root.after(100, self.update_status_loop)
    
    def update_status_indicator(self):
        """Actualizar el indicador de estado visual"""
        self.status_indicator.delete("all")
        
        if self.is_listening:
            color = '#4caf50'  # Verde - Escuchando
            text = "Escuchando..."
        elif self.is_processing:
            color = '#ff9800'  # Naranja - Procesando
            text = "Procesando..."
        elif self.is_speaking:
            color = '#2196f3'  # Azul - Hablando
            text = "Hablando..."
        else:
            color = '#757575'  # Gris - Inactivo
            text = "Listo"
        
        # Dibujar círculo de estado
        self.status_indicator.create_oval(5, 5, 15, 15, fill=color, outline="")
        self.status_label.config(text=text)
        
        # Actualizar visualizador de audio
        self.update_audio_visualizer()
    
    def update_audio_visualizer(self):
        """Actualizar visualizador de audio"""
        self.audio_visualizer.delete("all")
        
        if self.is_listening or self.is_speaking:
            # Simular ondas de audio
            for i in range(5):
                height = 5 + (i * 2) if self.is_listening else 3
                self.audio_visualizer.create_rectangle(
                    i * 20, 10 - height, i * 20 + 15, 10 + height,
                    fill='#4caf4f', outline=""
                )
    
    def toggle_listening(self):
        """Alternar modo de escucha"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """Iniciar escucha"""
        self.is_listening = True
        self.mic_button.config(text="🔴 Detener Escucha")
        
        # Iniciar reconocimiento en hilo separado
        threading.Thread(target=self.listen_for_speech, daemon=True).start()
    
    def stop_listening(self):
        """Detener escucha"""
        self.is_listening = False
        self.mic_button.config(text="🎤 Iniciar Escucha")
    
    def listen_for_speech(self):
        """Escuchar y procesar voz"""
        try:
            # Escuchar comando de voz
            command = self.voice_service.listen()
            
            if command:
                self.add_to_chat("Tú", command, 'user')
                self.process_command(command)
            else:
                self.add_to_chat("Sistema", "No se detectó voz", 'system')
                
        except Exception as e:
            self.add_to_chat("Error", str(e), 'error')
        finally:
            self.stop_listening()
    
    def process_command(self, command):
        """Procesar comando con IA"""
        self.is_processing = True
        
        try:
            # Procesar con IA
            response = self.ai_service.process_command(command)
            
            # Mostrar respuesta
            self.add_to_chat("Asistente", response, 'assistant')
            
            # Reproducir audio
            self.speak_response(response)
            
        except Exception as e:
            self.add_to_chat("Error", f"Error al procesar: {str(e)}", 'error')
        finally:
            self.is_processing = False
    
    def speak_response(self, text):
        """Reproducir respuesta por voz"""
        self.is_speaking = True
        
        try:
            # Reproducir en hilo separado
            threading.Thread(
                target=self.voice_service.speak, 
                args=(text,),
                daemon=True
            ).start()
            
            # Simular tiempo de habla (en una implementación real, esto se sincronizaría con el audio)
            time.sleep(len(text) * 0.05)
            
        except Exception as e:
            self.add_to_chat("Error", f"Error al hablar: {str(e)}", 'error')
        finally:
            self.is_speaking = False
    
    def add_to_chat(self, speaker, message, tag):
        """Añadir mensaje al chat"""
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{speaker}: {message}\n\n", tag)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def open_text_input(self):
        """Abrir ventana para entrada de texto"""
        text_window = tk.Toplevel(self.root)
        text_window.title("Entrada de Texto")
        text_window.geometry("300x200")
        text_window.configure(bg='#1a1a1a')
        
        tk.Label(text_window, text="Escribe tu mensaje:", 
                bg='#1a1a1a', fg='white').pack(pady=10)
        
        text_entry = tk.Text(text_window, height=6, bg='#2d2d2d', fg='white')
        text_entry.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        def send_text():
            text = text_entry.get("1.0", tk.END).strip()
            if text:
                self.add_to_chat("Tú", text, 'user')
                self.process_command(text)
                text_window.destroy()
        
        ttk.Button(text_window, text="Enviar", command=send_text).pack(pady=10)
    
    def open_settings(self):
        """Mostrar/ocultar panel de configuración"""
        if self.settings_visible:
            self.settings_frame.pack_forget()
            self.settings_visible = False
        else:
            self.settings_frame.pack(fill=tk.X, pady=(0, 10))
            self.settings_visible = True
    
    def clear_chat(self):
        """Limpiar área de chat"""
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete("1.0", tk.END)
        self.chat_area.config(state=tk.DISABLED)
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()

# Punto de entrada
if __name__ == "__main__":
    assistant = ModernAssistant()
    assistant.run()