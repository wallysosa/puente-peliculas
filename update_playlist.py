import subprocess
import os

# CONFIGURACIÓN DE CANALES
canales_yt = {
    "América TV":        ["https://www.youtube.com/@americaenvivo/live",   "https://i.imgur.com/uRj0S9m.png",  "ARGENTINA"],
    "A24":               ["https://www.youtube.com/@a24com/live",           "https://i.imgur.com/66Yv0vR.png",  "ARGENTINA"],
    "Crónica TV":        ["https://www.youtube.com/@cronicatv/live",        "https://i.imgur.com/L3pE1rK.png",  "ARGENTINA"],
    "Canal 26":          ["https://www.youtube.com/@Canal26/live",          "https://i.imgur.com/pYI8W0M.png",  "ARGENTINA"],
    "C5N":               ["https://www.youtube.com/@c5n/live",              "https://i.imgur.com/39hN3L3.png",  "ARGENTINA"],
    "TN Todo Noticias":  ["https://www.youtube.com/@todonoticias/live",     "https://i.imgur.com/Ossaqdt.png",  "ARGENTINA"],
    "TV Pública":        ["https://www.youtube.com/@TVPublicaArgentina/live","https://i.imgur.com/JkTjgIg.png", "ARGENTINA"],
    "La Nación+":        ["https://www.youtube.com/@lanacionmas/live",      "https://i.imgur.com/43LNplus.png", "ARGENTINA"],
    "Telefe Noticias":   ["https://www.youtube.com/@telefenoticias/live",   "https://i.imgur.com/dF9Tele.png",  "ARGENTINA"],
    "RTVE Noticias 24h": ["https://www.youtube.com/@rtve/live",             "https://i.imgur.com/8bCanal.png",  "ESPAÑA"],
    "DW Español":        ["https://www.youtube.com/@dwespanol/live",        "https://i.imgur.com/LAJoz4E.png",  "LATAM"],
}

def get_m3u8(url: str, cookie_file: str = "cookies.txt") -> str | None:
    cmd = [
        "yt-dlp",
        "--get-url",
        # Prioriza HLS (m3u8) nativo, si no hay cae al mejor disponible
        "--format", "bestvideo[protocol=m3u8_native]/bestvideo/best",
        "--user-agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36",
        "--no-check-certificates",
        "--no-warnings",
        "--cookies", cookie_file,
        url,
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=90
        )
        # yt-dlp puede devolver varias líneas; tomamos la primera válida
        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if "googlevideo.com" in line or ".m3u8" in line or line.startswith("http"):
                return line
        print(f"  [!] Respuesta inesperada de yt-dlp:\n{result.stdout[:200]}")
        return None
    except subprocess.TimeoutExpired:
        print(f"  [!] Timeout: {url}")
    except subprocess.CalledProcessError as e:
        print(f"  [!] Error yt-dlp: {e.stderr.strip()[:300]}")
    except FileNotFoundError:
        print("  [!] yt-dlp no encontrado. Instalalo con: pip install yt-dlp")
    return None


def main():
    cookie_file = "cookies.txt"

    if not os.path.exists(cookie_file):
        print(f"ERROR: No se encontró {cookie_file}")
        return
    if os.path.getsize(cookie_file) == 0:
        print(f"ERROR: {cookie_file} está vacío")
        return

    print(f"Usando cookies: {cookie_file}")
    print(f"Canales a procesar: {len(canales_yt)}\n")

    contenido = "#EXTM3U\n"
    encontrados = 0

    for nombre, (url, logo, grupo) in canales_yt.items():
        print(f"→ {nombre}")
        link = get_m3u8(url, cookie_file)
        if link:
            print(f"  ✓ OK")
            contenido += (
                f'#EXTINF:-1 tvg-logo="{logo}" group-title="{grupo}", {nombre}\n'
                f'{link}\n'
            )
            encontrados += 1
        else:
            print(f"  ✗ Falló")

    with open("lista_total.m3u", "w", encoding="utf-8") as f:
        f.write(contenido)

    print(f"\nFinalizado: {encontrados}/{len(canales_yt)} canales en lista_total.m3u")


if __name__ == "__main__":
    main()
