import subprocess
import os

# CONFIGURACIÓN DE CANALES (YouTube Live)
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
    "El País": ["https://www.youtube.com/@elpais/live", "https://i.imgur.com/02ElPais.png", "ESPAÑA"],
    "DW Español": ["https://www.youtube.com/@dwespanol/live", "https://i.imgur.com/LAJoz4E.png", "LATAM"],
    "France 24": ["https://www.youtube.com/@France24Espanol/live", "https://i.imgur.com/d4F24.png", "LATAM"],
    "TeleSUR": ["https://www.youtube.com/@telesur/live", "https://i.imgur.com/b3Telesur.png", "LATAM"]
}

def get_m3u8(url):
    try:
        # Comando optimizado para evitar bloqueos en servidores cloud
        result = subprocess.run(
            [
                'yt-dlp', 
                '-g', 
                '--format', 'best', 
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '--no-check-certificates',
                '--quiet',
                '--no-warnings',
                url
            ],
            capture_output=True, text=True, check=True, timeout=40
        )
        link = result.stdout.strip()
        # Verificamos que el link sea válido (googlevideo o m3u8 directo)
        return link if "googlevideo.com" in link or "m3u8" in link else None
    except Exception as e:
        print(f"Error extrayendo {url}: {e}")
        return None

def main():
    print("Iniciando generación de lista...")
    contenido = "#EXTM3U\n"
    encontrados = 0

    for nombre, info in canales_yt.items():
        print(f"Buscando enlace para: {nombre}")
        link_directo = get_m3u8(info[0])
        
        if link_directo:
            contenido += f'#EXTINF:-1 tvg-logo="{info[1]}" group-title="{info[2]}", {nombre}\n'
            contenido += f'{link_directo}\n'
            encontrados += 1
        else:
            print(f"Fallo al obtener enlace para {nombre}")

    # Guardar el archivo final que leerá tu App (ej. Kodi o VLC)
    with open("lista_total.m3u", "w", encoding="utf-8") as f:
        f.write(contenido)
    
    print(f"\n¡Proceso finalizado! Canales en la lista: {encontrados}")

if __name__ == "__main__":
    main()
