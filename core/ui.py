import sys
import io

class UI:
    # --- ANSI COLORS ---
    G = "\033[92m"  # Green
    R = "\033[91m"  # Red
    B = "\033[94m"  # Blue
    C = "\033[96m"  # Cyan
    Y = "\033[93m"  # Yellow
    M = "\033[95m"  # Magenta
    RESET = "\033[0m"

    @staticmethod
    def setup_terminal():
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    @classmethod
    def print_banner(cls):
        banner = f"""
        {cls.C} ██▒   █▓ ▒█████   ██▀███  ▄▄▄█████▓▓█████  ▒██   ██▒
        ▓██░   █▒▒██▒  ██▒▓██ ▒ ██▒▓  ██▒ ▓▒▓█   ▀  ▒▒ █ █ ▒░
         ▓██  █▒░▒██░  ██▒▓██ ░▄█ ▒▒ ▓██░ ▒░▒███    ░░  █   ░
          ▒██ █░░▒██   ██░▒██▀▀█▄  ░ ▓██▓ ░ ▒▓█  ▄   ▒████   ░
           ▒▀█░  ░ ████▓▒░░██▓ ▒██▒  ▒██▒ ░ ░▒████▒ ▒██▒ ▒██▒
           ░ ▐░  ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░  ▒ ░░   ░░ ▒░ ░ ▒▒ ░ ░▓ ░
           ░ ░░    ░ ▒ ▒░   ░▒ ░ ▒░    ░     ░ ░  ░ ░░   ░▒ ░
             ░░  ░ ░ ░ ▒    ░░   ░   ░         ░     ░    ░  
              ░      ░ ░     ░                 ░  ░  ░    ░  
             ░                                               {cls.RESET}
        """
        print(banner)

    @classmethod
    def info(cls, msg):
        print(f"{cls.G}[+]{cls.RESET} {msg}")

    @classmethod
    def error(cls, msg):
        print(f"{cls.R}[-]{cls.RESET} {msg}")

    @classmethod
    def warning(cls, msg):
        print(f"{cls.Y}[!]{cls.RESET} {msg}")

    @classmethod
    def highlight(cls, label, value):
        print(f"{cls.C}{label}:{cls.RESET} {value}")

    @classmethod
    def print_audit_report(cls, veredito, analise, confiança, trechos=None):
        """Exibe um relatório de auditoria em formato técnico e profissional."""
        
        # Cores para o status
        v_color = cls.G
        if "[FALSO]" in veredito.upper(): v_color = cls.R
        elif "[PARCIALMENTE" in veredito.upper(): v_color = cls.Y
        elif "[INCONCLUSIVO" in veredito.upper(): v_color = cls.M

        divider = "-" * 65
        
        print(f"\n{divider}")
        print(f"RESUMO DA AUDITORIA | VORTEX ENGINE")
        print(f"{divider}")
        
        print(f"STATUS DA ALEGAÇÃO: {v_color}{veredito}{cls.RESET}")
        print(f"CERTEZA DOCUMENTAL: {confiança}%")
        
        print(f"\nPARECER TÉCNICO:")
        import textwrap
        wrapper = textwrap.TextWrapper(width=65, initial_indent="  ", subsequent_indent="  ")
        for line in wrapper.wrap(analise):
            print(line)
            
        if trechos and len(trechos) > 0:
            print(f"\nELEMENTOS DE REFERÊNCIA:")
            for t in trechos:
                # Remove aspas se o LLM tiver colocado
                clean_t = t.strip('"').strip("'")
                for lt in wrapper.wrap(f"> {clean_t}"):
                    print(lt)

        print(f"{divider}\n")
