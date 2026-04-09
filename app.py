import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, Response

app = Flask(__name__)

@app.route('/lista.m3u')
def generar_m3u():
    # Intentamos con el Sitemap, que es lo más estructurado que tienen
    sitemap_url = "https://www.peelink2.com/post-sitemap.xml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://www.google.com/'
    }
    
    m3u_content = "#EXTM3U\n\n"
    
    try:
        # 1. Obtenemos las URLs del sitemap
        r = requests.get(sitemap_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, 'xml')
        # Filtramos las últimas 15 películas para no saturar tu RAM de 4GB
        urls = [loc.text for loc in soup.find_all('loc')][:15]
        
        for url in urls:
            try:
                # 2. Entramos a cada película
                res = requests.get(url, headers=headers, timeout=10)
                html = res.text
                
                # 3. Buscamos Vimeos, pero también otros servidores comunes si falla
                # El regex busca cualquier cosa que parezca un ID de video en vimeos.net
                vimeo_match = re.search(r'https?://vimeos\.net/embed/[\w-]+', html)
                
                if vimeo_match:
                    link = vimeo_match.group(0)
                    # Sacamos el título de la URL de forma elegante
                    titulo = url.split('/')[-1].replace('.html', '').replace('-', ' ').title()
                    
                    # Buscamos si hay una imagen (póster) en el código
                    img_match = re.search(r'https?://[^"\'\s]+\.(?:jpg|png|jpeg)', html)
                    poster = img_match.group(0) if img_match else ""

                    m3u_content += f'#EXTINF:-1 tvg-logo="{poster}", {titulo}\n'
                    m3u_content += f"{link}\n\n"
            except:
                continue
                
    except Exception as e:
        m3u_content += f"#EXTINF:-1, Error de conexion: {str(e)}\n"
        m3u_content += "https://vimeos.net/embed/error\n"

    # Si al final no encontró nada, ponemos un canal de relleno para que la lista no sea 0kb
    if len(m3u_content) < 20:
        m3u_content += "#EXTINF:-1, [Mantenimiento] Reintentar mas tarde\n"
        m3u_content += "https://vimeos.net/embed/mantenimiento\n"

    return Response(m3u_content, mimetype='audio/x-mpegurl')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
