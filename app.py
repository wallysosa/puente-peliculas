import os
import requests
import re
from flask import Flask, Response

app = Flask(__name__)

# Headers para engañar al servidor de video
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://ibelin.site/',
    'Origin': 'https://ibelin.site'
}

def obtener_link_fresco():
    url_peli = "https://www.peelink2.com/2025/12/ver-avatar-fuego-y-ceniza-2025-gratis.html"
    try:
        # 1. Entramos a la web de la peli
        r = requests.get(url_peli, headers={'User-Agent': HEADERS['User-Agent']}, timeout=10)
        
        # 2. Buscamos el ID del video en el código (está en los iframes que me pasaste)
        # Buscamos la URL de peliculasrey
        match = re.search(r'https://www\.peliculasrey\.me/red2\.php/([a-zA-Z0-9]+)', r.text)
        
        if match:
            # Si lo hallamos, devolvemos el link del reproductor
            # A veces la TV puede reproducir el link del iframe directamente
            return match.group(0)
            
    except Exception as e:
        print(f"Error: {e}")
    return None

@app.route('/lista.m3u')
def generar_m3u():
    link = obtener_link_fresco()
    
    m3u = "#EXTM3U\n"
    if link:
        m3u += "#EXTINF:-1, Avatar: Fuego y Ceniza (Enlace Actualizado)\n"
        m3u += f"{link}\n"
    else:
        m3u += "#EXTINF:-1, [Error] No se pudo renovar el enlace\n"
        m3u += "https://vimeos.net/error\n"
        
    return Response(m3u, mimetype='audio/x-mpegurl')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
