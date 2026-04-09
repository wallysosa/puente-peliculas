import cloudscraper
import re
from flask import Flask, Response

app = Flask(__name__)

@app.route('/lista.m3u')
def generar_m3u():
    # Usamos cloudscraper para saltar protecciones de Cloudflare/Bots
    scraper = cloudscraper.create_scraper()
    
    # Intentamos leer la portada directamente
    url_fuente = "https://www.peelink2.com/"
    
    m3u_content = "#EXTM3U\n\n"
    
    try:
        # 1. Obtenemos el HTML de la portada
        response = scraper.get(url_fuente, timeout=15)
        html = response.text
        
        # 2. Buscamos todas las URLs de posts de películas (ej: /2026/04/pelicula.html)
        # Usamos un Set para no repetir películas
        enlaces = set(re.findall(r'https://www\.peelink2\.com/20\d{2}/\d{2}/[^"\'>]+\.html', html))
        
        # 3. Procesamos las primeras 10 para que sea rápido
        for url in list(enlaces)[:10]:
            try:
                res_peli = scraper.get(url, timeout=10)
                peli_html = res_peli.text
                
                # Buscamos el ID de Vimeo
                vimeo_match = re.search(r'https?://vimeos\.net/embed/[\w-]+', peli_html)
                
                if vimeo_match:
                    video_link = vimeo_match.group(0)
                    # Título limpio desde la URL
                    titulo = url.split('/')[-1].replace('.html', '').replace('-', ' ').title()
                    
                    m3u_content += f'#EXTINF:-1, {titulo}\n'
                    m3u_content += f"{video_link}\n\n"
            except:
                continue

    except Exception as e:
        print(f"Error: {e}")

    # Si sigue vacío, al menos ponemos un link que funcione para probar la TV
    if m3u_content == "#EXTM3U\n\n":
        m3u_content += "#EXTINF:-1, [AVISO] El sitio esta bajo proteccion fuerte. Reintenta en 5 min.\n"
        m3u_content += "https://vimeos.net/embed/espera\n"

    return Response(m3u_content, mimetype='audio/x-mpegurl')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
