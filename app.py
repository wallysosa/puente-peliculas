import os
import requests
import re
from flask import Flask, Response

app = Flask(__name__)

# Usamos los datos exactos que capturaste para que el sitio no sospeche
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'es-US,es-ES;q=0.9,es;q=0.8',
    'Referer': 'https://www.peelink2.com/',
    'Origin': 'https://ibelin.site'
}

def extraer_m3u8_manual():
    url_peli = "https://www.peelink2.com/2025/12/ver-avatar-fuego-y-ceniza-2025-gratis.html"
    
    try:
        # 1. Entramos a la página de la película
        sesion = requests.Session()
        r = sesion.get(url_peli, headers=HEADERS, timeout=15)
        html = r.text

        # 2. Buscamos el link de peliculasrey que es el que genera el stream
        # El HTML que pasaste tiene iframes con este formato
        iframe_match = re.search(r'https://www\.peliculasrey\.me/red2\.php/[a-zA-Z0-9]+', html)
        
        if iframe_match:
            iframe_url = iframe_match.group(0)
            # Entramos al iframe para que nos suelte la galleta (cookie) y el video
            r_video = sesion.get(iframe_url, headers=HEADERS, timeout=15)
            
            # 3. Buscamos el link .m3u8 directamente en el código del reproductor
            # Usamos el patrón que encontraste de globalcdn
            video_match = re.search(r'https://[a-z0-9.]+\.cfglobalcdn\.com/[^"\'>]+\.m3u8', r_video.text)
            
            if video_match:
                return video_match.group(0)
                
        # Si no lo halla por regex, intentamos buscar el link que me pasaste antes
        # que suele estar en los scripts de la página
        backup_match = re.search(r'https?://[^\s"\'<>]+?\.m3u8', html)
        if backup_match:
            return backup_match.group(0)

    except Exception as e:
        print(f"Error: {e}")
    
    return None

@app.route('/lista.m3u')
def generar_lista():
    link_directo = extraer_m3u8_manual()
    
    m3u = "#EXTM3U\n"
    if link_directo:
        m3u += "#EXTINF:-1, Avatar 3 (Stream Directo)\n"
        m3u += f"{link_directo}\n"
    else:
        # Link de emergencia si falla la extracción automática
        m3u += "#EXTINF:-1, [Mantenimiento] El sitio cambio seguridad\n"
        m3u += "https://vimeos.net/null\n"
        
    return Response(m3u, mimetype='audio/x-mpegurl')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
