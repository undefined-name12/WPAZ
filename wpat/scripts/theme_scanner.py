import requests
import time
import signal
import sys
from random import uniform
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}WORDPRESS THEME SCANNER {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
{Style.RESET_ALL}"""

shutdown = False

def handle_sigint(signum, frame):
    global shutdown
    if not shutdown:
        shutdown = True
        print(f"\n{Fore.RED}[!]{Style.RESET_ALL} Escaneo cancelado")
        sys.exit(1)

signal.signal(signal.SIGINT, handle_sigint)

def cargar_wordlist(ruta):
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(ruta, 'r', encoding=encoding, errors='strict') as f:
                contenido = f.read()
                print(f"{Fore.GREEN}✅ Encoding detectado: {encoding}{Style.RESET_ALL}")
                return [linea.strip() for linea in contenido.splitlines() if linea.strip()], len(contenido.splitlines())
        except UnicodeDecodeError:
            continue
    
    try:
        with open(ruta, 'r', encoding='latin-1', errors='replace') as f:
            lineas = f.readlines()
            print(f"{Fore.YELLOW}⚠️  Usando encoding latín-1 con reemplazo{Style.RESET_ALL}")
            return [linea.strip() for linea in lineas if linea.strip()], len(lineas)
    except Exception as e:
        raise ValueError(f"Error de carga: {str(e)}")

def check_theme(target_url, theme, timeout=15):
    global shutdown
    if shutdown:
        return ("cancelled", None)
    
    headers = {'User-Agent': 'WP Audit Tool'}
    url = f"{target_url.rstrip('/')}/wp-content/themes/{theme}/"
    
    try:
        time.sleep(uniform(0.01, 0.05))
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=False)
        
        if response.status_code == 200:
            return ("found", theme)
        elif response.status_code == 403:
            readme_url = f"{url}style.css"
            readme_response = requests.head(readme_url, headers=headers, timeout=timeout)
            return ("found", theme) if readme_response.status_code == 200 else ("possible", theme)
            
    except requests.exceptions.RequestException as e:
        return ("error", f"{theme}: {str(e)}")
    
    return ("not_found", theme)

def scan_themes(url):
    global shutdown
    shutdown = False

    print(BANNER)
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Wordlist de temas (ruta): ", end="")
    wordlist_path = input().strip()
    
    try:
        start_time = time.time()
        themes, total_lineas = cargar_wordlist(wordlist_path)
        tiempo_carga = time.time() - start_time
        print(f"{Fore.CYAN}[i] {total_lineas} temas cargados en {tiempo_carga:.2f}s{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")
        return
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Hilos (10): ", end="")
    threads = input().strip() or "10"
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Timeout (15s): ", end="")
    timeout = input().strip() or "15"
    
    threads = int(threads)
    timeout = int(timeout)

    found = []
    possible = []
    errors = []

    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(check_theme, url, theme, timeout) for theme in themes]
            
            with tqdm(
                total=len(themes),
                desc=f"{Fore.CYAN}⏳ Escaneando temas{Style.RESET_ALL}",
                unit="tema",
                dynamic_ncols=True,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
            ) as pbar:
                for future in as_completed(futures):
                    if shutdown:
                        break
                    result_type, data = future.result()
                    
                    if result_type == "found":
                        found.append(data)
                        pbar.write(f"{Fore.GREEN}✅ {data}{Style.RESET_ALL}")
                    elif result_type == "possible":
                        possible.append(data)
                        pbar.write(f"{Fore.YELLOW}⚠️  {data} (403){Style.RESET_ALL}")
                    elif result_type == "error":
                        errors.append(data)
                        pbar.write(f"{Fore.RED}⚠️  {data}{Style.RESET_ALL}")
                    
                    pbar.update(1)

    except KeyboardInterrupt:
        shutdown = True
        print(f"\n{Fore.RED}[!] Escaneo interrumpido{Style.RESET_ALL}")
    finally:
        print("\033[K", end="")

    print(f"\n{Style.BRIGHT}{Fore.CYAN}►► {Fore.WHITE}RESULTADOS")
    print(f"{Fore.CYAN}├───────────────{Fore.WHITE}───────────────────────┤")
    print(f"{Fore.CYAN}│ {Fore.GREEN}✔ Detectados: {Fore.WHITE}{len(found):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.YELLOW}⚠ Posibles:  {Fore.WHITE}{len(possible):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.RED}☠ Errores:   {Fore.WHITE}{len(errors):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}└───────────────{Fore.WHITE}───────────────────────┘\n")

def scan_themes_gui(url):
    global shutdown
    shutdown = False

    print(BANNER)
    
    # Valores por defecto automáticos
    wordlist_path = "wordlists/temas.txt"
    threads = 10
    timeout = 15

    try:
        start_time = time.time()
        themes, total_lineas = cargar_wordlist(wordlist_path)
        tiempo_carga = time.time() - start_time
        print(f"{Fore.CYAN}[i] {total_lineas} temas cargados en {tiempo_carga:.2f}s{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")
        return
    
    found = []
    possible = []
    errors = []

    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(check_theme, url, theme, timeout) for theme in themes]
            
            with tqdm(
                total=len(themes),
                desc=f"{Fore.CYAN}⏳ Escaneando temas{Style.RESET_ALL}",
                unit="tema",
                dynamic_ncols=True,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
            ) as pbar:
                for future in as_completed(futures):
                    if shutdown:
                        break
                    result_type, data = future.result()
                    
                    if result_type == "found":
                        found.append(data)
                        pbar.write(f"{Fore.GREEN}✅ {data}{Style.RESET_ALL}")
                    elif result_type == "possible":
                        possible.append(data)
                        pbar.write(f"{Fore.YELLOW}⚠️  {data} (403){Style.RESET_ALL}")
                    elif result_type == "error":
                        errors.append(data)
                        pbar.write(f"{Fore.RED}⚠️  {data}{Style.RESET_ALL}")
                    
                    pbar.update(1)

    except KeyboardInterrupt:
        shutdown = True
        print(f"\n{Fore.RED}[!] Escaneo interrumpido{Style.RESET_ALL}")
    finally:
        print("\033[K", end="")

    print(f"\n{Style.BRIGHT}{Fore.CYAN}►► {Fore.WHITE}RESULTADOS")
    print(f"{Fore.CYAN}├───────────────{Fore.WHITE}───────────────────────┤")
    print(f"{Fore.CYAN}│ {Fore.GREEN}✔ Detectados: {Fore.WHITE}{len(found):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.YELLOW}⚠ Posibles:  {Fore.WHITE}{len(possible):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.RED}☠ Errores:   {Fore.WHITE}{len(errors):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}└───────────────{Fore.WHITE}───────────────────────┘\n")
