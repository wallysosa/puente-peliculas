import subprocess
import os

# CONFIGURACIÓN DE CANALES (YouTube Live)
# Formato: "Nombre": ["URL_YouTube", "Logo", "Grupo"]
canales_yt = {
    # --- ARGENTINA ---
    "América TV": ["https://www.youtube.com/@americaenvivo/live", "https://i.imgur.com/uRj0S9m.png", "ARGENTINA"],
    "A24": ["https://www.youtube.com/@a24com/live", "https://i.imgur.com/66Yv0vR.png", "ARGENTINA"],
    "Crónica TV": ["https://www.youtube.com/@cronicatv/live", "https://i.imgur.com/L3pE1rK.png", "ARGENTINA"],
    "Canal 26": ["https://www.youtube.com/@Canal26/live", "https://i.imgur.com/pYI8W0M.png", "ARGENTINA"],
    "C5N": ["https://www.youtube.com/@c5n/live", "https://i.imgur.com/39hN3L3.png", "ARGENTINA"],
    "TN Todo Noticias": ["https://www.youtube.com/@todonoticias/live", "https://i.imgur.com/Ossaqdt.png", "ARGENTINA"],
    "TV Pública": ["https://www.youtube.com/@TVPublicaArgentina/live", "https://i.imgur.com/JkTjgIg.png", "ARGENTINA"],
    "La Nación+": ["https://www.youtube.com/@lanacionmas/live", "https://i.imgur.com/43LNplus.png", "ARGENTINA"],
    "Telefe Noticias": ["https://www.youtube.com/@telefenoticias/live", "https://i.imgur.com/dF9Tele.png", "ARGENTINA"],
    
    # --- ESPAÑA ---
    "RTVE Noticias 24h": ["https://www.youtube.com/@rtve/live", "https://i.imgur.com/8bCanal.png", "ESPAÑA"],
    "El País": ["https://www.youtube.com/@elpais/live", "https://i.imgur.com/02ElPais.png", "ESPAÑA"],
    
    # --- MÉXICO ---
    "Foro TV": ["https://www.youtube.com/@nmas/live", "https://i.imgur.com/1aNLogo.png", "MÉXICO"],
    "Azteca Noticias": ["https://www.youtube.com/@AztecaNoticias/live", "https://i.imgur.com/7eAzteca.png", "MÉXICO"],
    "Milenio TV": ["https://www.youtube.com/@milenio/live", "https://i.imgur.com/30Milenio.png", "MÉXICO"],

    # --- LATAM ---
    "Noticias Caracol": ["https://www.youtube.com/@noticiascaracol/live", "https://i.imgur.com/wIINoSK.png", "COLOMBIA"],
    "T13 Chile": ["https://www.youtube.com/@teletrece/live", "https://i.imgur.com/6dTele13.png", "CHILE"],
    "DW Español": ["https://www.youtube.com/@dwespanol/live", "https://i.imgur.com/LAJoz4E.png", "LATAM"],
    "France 24": ["https://www.youtube.com/@France24Espanol/live", "https://i.imgur.com/d4F24.png", "LATAM"],
    "TeleSUR": ["https://www.youtube.com/@telesur/live", "https://i.imgur.com/b3Telesur.png", "LATAM"]
}

def get_m3u8(url):
    try:
        # Añadimos --quiet para no llenar el log y --no-warnings
        result = subprocess.run(
            ['yt-dlp', '-g', '--format', 'best', '--no-warnings', url],
            capture_output=True, text=True, check=True, timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error extrayendo {url}: {e}")
        return None

def main():
    # 1. Cargar la lista base (flow_base.m3u)
    if os.path.exists("flow_base.m3u"):
        with open("flow_base.m3u", "r", encoding="utf-8") as f:
            contenido = f.read().strip() + "\n"
    else:
        contenido = "#EXTM3U\n"

    contenido += "\n# --- CANALES ACTUALIZADOS (YOUTUBE LIVE) ---\n"

    # 2. Obtener links dinámicos de YouTube
    for nombre, info in canales_yt.items():
        print(f"Buscando link: {nombre}...")
        link_directo = get_m3u8(info[0])
        if link_directo:
            contenido += f'#EXTINF:-1 tvg-logo="{info[1]}" group-title="{info[2]}", {nombre}\n{link_directo}\n'

    # 3. Escribir el archivo final lista_total.m3u
    with open("lista_total.m3u", "w", encoding="utf-8") as f:
        f.write(contenido)
    print("¡Proceso terminado! Lista unificada creada con éxito.")

if __name__ == "__main__":
    main()
