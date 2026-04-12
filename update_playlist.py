import subprocess
import os

# CONFIGURACIÓN DE CANALES
canales_yt = {
    "América TV": ["https://www.youtube.com/@americaenvivo/live", "https://i.imgur.com/uRj0S9m.png", "ARGENTINA"],
    "A24": ["https://www.youtube.com/@a24com/live", "https://i.imgur.com/66Yv0vR.png", "ARGENTINA"],
    "Crónica TV": ["https://www.youtube.com/@cronicatv/live", "https://i.imgur.com/L3pE1rK.png", "ARGENTINA"],
    "Canal 26": ["https://www.youtube.com/@Canal26/live", "https://i.imgur.com/pYI8W0M.png", "ARGENTINA"],
    "C5N": ["https://www.youtube.com/@c5n/live", "https://i.imgur.com/39hN3L3.png", "ARGENTINA"],
    "TN Todo Noticias": ["https://www.youtube.com/@todonoticias/live", "https://i.imgur.com/Ossaqdt.png", "ARGENTINA"],
    "TV Pública": ["https://www.youtube.com/@TVPublicaArgentina/live", "https://i.imgur.com/JkTjgIg.png", "ARGENTINA"],
    "La Nación+": ["https://www.youtube.com/@lanacionmas/live", "https://i.imgur.com/43LNplus.png", "ARGENTINA"],
    "Telefe Noticias": ["https://www.youtube.com/@telefenoticias/live", "https://i.imgur.com/dF9Tele.png", "ARGENTINA"],
    "RTVE Noticias 24h": ["https://www.youtube.com/@rtve/live", "https://i.imgur.com/8bCanal.png", "ESPAÑA"],
    "DW Español": ["https://www.youtube.com/@dwespanol/live", "https://i.imgur.com/LAJoz4E.png", "LATAM"]
}

def get_m3u8(url):
    try:
        cookie_file = 'cookies.txt'
        # Usamos flags para forzar a yt-dlp a ser lo más parecido a un humano
        cmd = [
            'yt-dlp', 
            '--get-url',
            '--format', 'best',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--no-check-certificates',
            '--no-warnings'
        ]
        
        if os.path.exists(cookie_file):
            cmd.extend(['--cookies', cookie_file])
            
        cmd.append(url)
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        link = result.stdout.strip()
        return link if "googlevideo.com" in link or "m3u8" in link else None
    except Exception as e:
        print(f"Error extrayendo {url}: {e}")
        return None

def main():
    print("Iniciando generación con soporte de cookies...")
    contenido = "#EXTM3U\n"
    encontrados = 0

    for nombre, info in canales_yt.items():
        print(f"Procesando canal: {nombre}")
        link = get_m3u8(info[0])
        if link:
            contenido += f'#EXTINF:-1 tvg-logo="{info[1]}" group-title="{info[2]}", {nombre}\n{link}\n'
            encontrados += 1
        else:
            print(f" -> No se pudo obtener link para {nombre}")

    with open("lista_total.m3u", "w", encoding="utf-8") as f:
        f.write(contenido)
    
    print(f"\nLista creada con {encontrados} canales.")

if __name__ == "__main__":
    main()
