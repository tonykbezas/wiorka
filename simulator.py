import time
import random
import math
import threading
from dataclasses import dataclass
from typing import Callable, Optional
import pyautogui
from pynput import keyboard

# Safe PyAutoGUI settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

@dataclass
class SimulatorConfig:
    duration_seconds: float = 0.0  # 0 = Indefinido
    enable_mouse_move: bool = True
    enable_scroll: bool = True
    enable_tab_switch: bool = True
    enable_typing: bool = True
    enable_clicks: bool = False
    
    # Atajo de cambio de ventanas: "alt_tab" (Windows Apps), "ctrl_tab" (Navegador), "both"
    tab_mode: str = "alt_tab"
    
    # Hiper-realismo: Ráfagas de trabajo + Pausas humanas con temblor de mano
    enable_hyper_realism: bool = True
    
    # Intervalos en segundos para ciclos de ráfaga y lectura
    mouse_interval: tuple[float, float] = (3.0, 7.0)
    scroll_interval: tuple[float, float] = (4.0, 10.0)
    tab_interval: tuple[float, float] = (15.0, 40.0)
    typing_interval: tuple[float, float] = (8.0, 22.0)
    click_interval: tuple[float, float] = (25.0, 65.0)
    
    typing_mode: str = "safe"

class ActivitySimulator:
    def __init__(self, config: SimulatorConfig, 
                 log_callback: Optional[Callable[[str], None]] = None,
                 time_callback: Optional[Callable[[int], None]] = None,
                 status_callback: Optional[Callable[[str], None]] = None):
        self.config = config
        self.log_cb = log_callback or (lambda msg: print(f"[LOG] {msg}"))
        self.time_cb = time_callback or (lambda secs: None)
        self.status_cb = status_callback or (lambda st: None)
        
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._listener: Optional[keyboard.Listener] = None
        self.screen_w, self.screen_h = pyautogui.size()
        self.start_time = 0.0

    def start(self):
        """Inicia la simulación en un hilo secundario y el escucha de ESC."""
        if self.is_running:
            return
        
        self.is_running = True
        self.start_time = time.time()
        self.status_cb("running")
        self.log_cb("🚀 Simulador iniciado (Modo Hiper-Realista). Presiona 'ESC' o mueve el mouse a la esquina superior izquierda para detener.")

        self._listener = keyboard.Listener(on_press=self._on_key_press)
        self._listener.start()

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self, reason: str = "Detenido por el usuario"):
        """Detiene la simulación de manera segura."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self._listener and self._listener.running:
            self._listener.stop()
            
        self.status_cb("stopped")
        self.log_cb(f"🛑 Simulador detenido: {reason}")

    def _on_key_press(self, key):
        if key == keyboard.Key.esc:
            self.log_cb("⚠️ Tecla 'ESC' detectada. Ejecutando parada de emergencia...")
            self.stop(reason="Parada de emergencia (ESC)")

    def _run_loop(self):
        """Bucle principal con arquitectura de Ráfagas + Pausas de Lectura (Hiper-Realismo)."""
        last_mouse = time.time()
        last_scroll = time.time()
        last_tab = time.time()
        last_typing = time.time()
        last_click = time.time()

        next_mouse_delay = random.uniform(*self.config.mouse_interval)
        next_scroll_delay = random.uniform(*self.config.scroll_interval)
        next_tab_delay = random.uniform(*self.config.tab_interval)
        next_typing_delay = random.uniform(*self.config.typing_interval)
        next_click_delay = random.uniform(*self.config.click_interval)

        # Estado de ciclo hiper-realista: "active" (trabajando) o "thinking" (leyendo/pausa)
        cycle_state = "active"
        cycle_switch_time = time.time() + random.uniform(40.0, 90.0)

        while self.is_running:
            now = time.time()
            elapsed = now - self.start_time

            # Verificar temporizador límite
            if self.config.duration_seconds > 0:
                remaining = int(self.config.duration_seconds - elapsed)
                if remaining <= 0:
                    self.time_cb(0)
                    self.stop(reason="Tiempo completado exitosamente")
                    break
                else:
                    self.time_cb(remaining)

            # --- GESTIÓN DE CICLOS HIPER-REALISTAS ---
            if self.config.enable_hyper_realism:
                if now >= cycle_switch_time:
                    if cycle_state == "active":
                        cycle_state = "thinking"
                        pause_duration = random.uniform(15.0, 35.0)
                        cycle_switch_time = now + pause_duration
                        self.log_cb(f"🧠 Pausa de lectura/pensamiento ({int(pause_duration)}s) con micro-movimientos de descanso...")
                    else:
                        cycle_state = "active"
                        active_duration = random.uniform(45.0, 110.0)
                        cycle_switch_time = now + active_duration
                        self.log_cb(f"⚡ Reanudando ráfaga de navegación activa ({int(active_duration)}s)...")

            # --- EJECUCIÓN EN MODO PAUSA (THINKING) ---
            if cycle_state == "thinking" and self.config.enable_hyper_realism:
                # Durante la pausa de lectura, solo se realizan micro-temblores (1-3px) de la mano descansando sobre el mouse
                if random.random() < 0.25:  # Ocasionalmente
                    self._action_hand_tremor()
                time.sleep(random.uniform(2.5, 5.0))
                continue

            # --- EJECUCIÓN EN MODO ACTIVO (ACTIVE BURST) ---

            # 1. Movimiento del Mouse
            if self.config.enable_mouse_move and (now - last_mouse >= next_mouse_delay):
                self._action_move_mouse()
                last_mouse = time.time()
                next_mouse_delay = random.uniform(*self.config.mouse_interval)

            # 2. Scroll de lectura
            if self.is_running and self.config.enable_scroll and (now - last_scroll >= next_scroll_delay):
                self._action_scroll()
                last_scroll = time.time()
                next_scroll_delay = random.uniform(*self.config.scroll_interval)

            # 3. Cambio de pestañas / ventanas (Alt+Tab / Ctrl+Tab)
            if self.is_running and self.config.enable_tab_switch and (now - last_tab >= next_tab_delay):
                self._action_tab_switch()
                last_tab = time.time()
                next_tab_delay = random.uniform(*self.config.tab_interval)

            # 4. Tecleo de teclado
            if self.is_running and self.config.enable_typing and (now - last_typing >= next_typing_delay):
                self._action_typing()
                last_typing = time.time()
                next_typing_delay = random.uniform(*self.config.typing_interval)

            # 5. Clics de mouse seguros
            if self.is_running and self.config.enable_clicks and (now - last_click >= next_click_delay):
                self._action_click()
                last_click = time.time()
                next_click_delay = random.uniform(*self.config.click_interval)

            time.sleep(0.2)

    # --- ACCIONES INDIVIDUALES HIPER-REALISTAS ---

    def _action_hand_tremor(self):
        """Simula el micro-temblor o respiración de la mano descansando sobre el mouse (1 a 3 píxeles)."""
        try:
            cur_x, cur_y = pyautogui.position()
            dx = random.choice([-2, -1, 1, 2])
            dy = random.choice([-2, -1, 1, 2])
            new_x = max(10, min(self.screen_w - 10, cur_x + dx))
            new_y = max(10, min(self.screen_h - 10, cur_y + dy))
            pyautogui.moveTo(new_x, new_y, duration=0.15)
        except Exception:
            pass

    def _action_move_mouse(self):
        """Mueve el mouse siguiendo una curva de Bézier suave y natural."""
        try:
            start_x, start_y = pyautogui.position()
            margin = 120
            target_x = random.randint(margin, self.screen_w - margin)
            target_y = random.randint(margin, self.screen_h - margin)

            ctrl_x1 = start_x + random.randint(-180, 180)
            ctrl_y1 = start_y + random.randint(-180, 180)
            ctrl_x2 = target_x + random.randint(-180, 180)
            ctrl_y2 = target_y + random.randint(-180, 180)

            steps = random.randint(25, 40)
            duration = random.uniform(0.5, 1.2)
            dt = duration / steps

            self.log_cb(f"🖱️ Moviendo cursor hacia ({target_x}, {target_y})...")

            for i in range(steps + 1):
                if not self.is_running:
                    break
                t = i / steps
                b_x = ((1 - t)**3 * start_x + 
                       3 * (1 - t)**2 * t * ctrl_x1 + 
                       3 * (1 - t) * t**2 * ctrl_x2 + 
                       t**3 * target_x)
                
                b_y = ((1 - t)**3 * start_y + 
                       3 * (1 - t)**2 * t * ctrl_y1 + 
                       3 * (1 - t) * t**2 * ctrl_y2 + 
                       t**3 * target_y)

                pyautogui.moveTo(int(b_x), int(b_y))
                time.sleep(dt)

        except pyautogui.FailSafeException:
            self.stop("FailSafe activado (Mouse en la esquina superior izquierda)")
        except Exception as e:
            self.log_cb(f"⚠️ Error en movimiento de mouse: {e}")

    def _action_scroll(self):
        """Simula lectura desplazando la página progresivamente."""
        try:
            scroll_amount = random.randint(-350, -150)
            self.log_cb(f"📜 Desplazando página (scroll down {abs(scroll_amount)} px)...")
            
            steps = random.randint(3, 5)
            sub_scroll = int(scroll_amount / steps)
            for _ in range(steps):
                if not self.is_running:
                    break
                pyautogui.scroll(sub_scroll)
                time.sleep(random.uniform(0.1, 0.25))

            if random.random() < 0.25 and self.is_running:
                time.sleep(random.uniform(0.6, 1.4))
                pyautogui.scroll(random.randint(60, 160))
                self.log_cb("📜 Leve retroceso de lectura (scroll up)...")

        except pyautogui.FailSafeException:
            self.stop("FailSafe activado")
        except Exception as e:
            self.log_cb(f"⚠️ Error en scroll: {e}")

    def _action_tab_switch(self):
        """Cambia entre ventanas (Alt+Tab) o pestañas (Ctrl+Tab) en Windows."""
        try:
            mode = self.config.tab_mode
            if mode == "both":
                mode = random.choice(["alt_tab", "ctrl_tab"])

            if mode == "alt_tab":
                self.log_cb("🪟 Cambiando de ventana activa (Alt + Tab)...")
                pyautogui.keyDown('alt')
                time.sleep(0.12)
                pyautogui.press('tab')
                time.sleep(0.12)
                pyautogui.keyUp('alt')
            else:
                self.log_cb("📑 Cambiando de pestaña (Ctrl + Tab)...")
                pyautogui.hotkey('ctrl', 'tab')

        except pyautogui.FailSafeException:
            self.stop("FailSafe activado")
        except Exception as e:
            self.log_cb(f"⚠️ Error al cambiar de ventana/pestaña: {e}")

    def _action_typing(self):
        """Simula pulsación de teclas o tecleo inofensivo."""
        try:
            if self.config.typing_mode == "safe":
                key = random.choice(['shift', 'down', 'up', 'ctrl'])
                if key in ['shift', 'ctrl']:
                    self.log_cb(f"⌨️ Pulsación de presencia (Tecla {key.capitalize()})...")
                    pyautogui.press(key)
                else:
                    self.log_cb(f"⌨️ Navegando documento (Tecla {key.capitalize()})...")
                    pyautogui.press(key)
            else:
                text_snippets = [
                    "Revisando reporte...",
                    "Analizando datos.",
                    "Verificando avances."
                ]
                snippet = random.choice(text_snippets)
                self.log_cb("⌨️ Escribiendo notas simuladas...")
                pyautogui.typewrite(snippet, interval=random.uniform(0.06, 0.14))

        except pyautogui.FailSafeException:
            self.stop("FailSafe activado")
        except Exception as e:
            self.log_cb(f"⚠️ Error en simulación de tecleo: {e}")

    def _action_click(self):
        """Realiza un clic seguro en la posición actual."""
        try:
            self.log_cb("🖱️ Clic de ratón seguro...")
            pyautogui.click()
        except pyautogui.FailSafeException:
            self.stop("FailSafe activado")
        except Exception as e:
            self.log_cb(f"⚠️ Error en clic: {e}")
