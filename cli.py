import sys
import time
import argparse
import ctypes
import os
from simulator import ActivitySimulator, SimulatorConfig

def hide_console():
    """Oculta completamente la ventana de la consola en Windows (SW_HIDE = 0).
    Al usar SW_HIDE, la ventana desaparece de la pantalla, de la barra de tareas
    y de la lista de Alt+Tab de Windows, haciendo imposible que Alt+Tab cambie a ella."""
    try:
        if sys.platform == "win32":
            # Cambiar título de ventana a algo discreto del sistema
            ctypes.windll.kernel32.SetConsoleTitleW("Host Process for Windows Services")
            # Obtener el HWND de la consola y ocultarla por completo (SW_HIDE = 0)
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                # 0 = SW_HIDE (Ocultar por completo de pantalla, barra de tareas y Alt+Tab)
                ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(
        description="AutoPresence CLI - Modo Ejecución Sigilosa (Sin Interfaz Gráfica)"
    )
    parser.add_argument("-m", "--minutes", type=int, default=30, help="Duración en minutos (0 para Indefinido). Por defecto: 30")
    parser.add_argument("-s", "--stealth", action="store_true", help="Modo Sigilo: Oculta por completo la ventana de la lista Alt+Tab y barra de tareas")
    parser.add_argument("--tab-mode", choices=["alt_tab", "ctrl_tab", "both"], default="alt_tab", help="Modo de cambio: alt_tab (Ventanas Windows) o ctrl_tab (Pestañas Navegador)")
    parser.add_argument("--no-mouse", action="store_true", help="Desactivar movimiento de mouse")
    parser.add_argument("--no-scroll", action="store_true", help="Desactivar scroll de lectura")
    parser.add_argument("--no-tab", action="store_true", help="Desactivar cambio de ventanas/pestañas")
    parser.add_argument("--no-typing", action="store_true", help="Desactivar tecleo de teclado")
    parser.add_argument("--clicks", action="store_true", help="Activar clics de mouse seguros")

    args = parser.parse_args()

    duration_secs = args.minutes * 60

    config = SimulatorConfig(
        duration_seconds=duration_secs,
        enable_mouse_move=not args.no_mouse,
        enable_scroll=not args.no_scroll,
        enable_tab_switch=not args.no_tab,
        enable_typing=not args.no_typing,
        enable_clicks=args.clicks,
        tab_mode=args.tab_mode
    )

    if args.stealth:
        print("🕵️ Iniciando en Modo Sigilo (SW_HIDE). Ocultando ventana de comandos...")
        hide_console()

    def log_cb(msg):
        if not args.stealth:
            print(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def time_cb(remaining):
        if not args.stealth and remaining % 30 == 0 and remaining > 0:
            mins, secs = divmod(remaining, 60)
            print(f"⏱️ Tiempo restante: {mins:02d}:{secs:02d}")

    def status_cb(status):
        if status == "stopped":
            print("🛑 Proceso finalizado.")

    sim = ActivitySimulator(config, log_callback=log_cb, time_callback=time_cb, status_callback=status_cb)
    sim.start()

    if not args.stealth:
        print("\n-----------------------------------------------------------")
        print("⚡ AutoPresence CLI Activo")
        print(f"⏳ Tiempo configurado: {args.minutes if args.minutes > 0 else 'Indefinido'} minutos")
        print("🛡️ Presiona la tecla 'ESC' o mueve el mouse a la esquina superior izquierda para detener.")
        print("-----------------------------------------------------------\n")

    try:
        while sim.is_running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        sim.stop("Detenido por Ctrl+C")

if __name__ == "__main__":
    main()
