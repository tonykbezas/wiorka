import sys
import argparse
from gui import AutoPresenceGUI
import cli

def main():
    if len(sys.argv) > 1 and ("--cli" in sys.argv or "-m" in sys.argv or "--stealth" in sys.argv):
        # Redirigir a modo CLI si se pasan argumentos de consola
        cli.main()
    else:
        # Por defecto abrir GUI moderna
        try:
            app = AutoPresenceGUI()
            app.mainloop()
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Error al iniciar la interfaz gráfica: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
