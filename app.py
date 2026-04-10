import re, logging
from flask import Flask, Response
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def extraer_links_avatar():
    movie_url = "https://www.peelink2.com/2025/12/ver-avatar-fuego-y-ceniza-2025-gratis.html"
    streams = []
    
    with sync_playwright() as p:
        # Lanzamos el navegador [cite: 69]
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            logger.info(f"Navegando a: {movie_url}")
            page.goto(movie_url, wait_until='networkidle', timeout=30000) [cite: 72]
            html = page.content() [cite: 73]
            
            # Buscamos los enlaces que están dentro de los iframes que pasaste
            # El regex busca la estructura 'https://www.peliculasrey.me/red2.php/...'
            matches = re.findall(r'https://www\.peliculasrey\.me/red2\.php/[a-zA-Z0-9]+', html)
            
            for index, link in enumerate(matches, start=1):
                streams.append({
                    "titulo": f"Avatar: Fuego y Ceniza - Opcion {index}",
                    "url": link
                })
                
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            browser.close() [cite: 74]
            
    return streams

@app.route('/lista.m3u')
def generar_m3u():
    # Iniciamos la lista M3U [cite: 125]
    streams = extraer_links_avatar()
    
    m3u_content = "#EXTM3U\n\n"
    for s in streams:
        # Añadimos cada opción encontrada [cite: 136-137]
        m3u_content += f"#EXTINF:-1, {s['titulo']}\n"
        m3u_content += f"{s['url']}\n\n"
    
    if not streams:
        m3u_content += "#EXTINF:-1, No se encontraron enlaces\nhttps://vimeos.net/null\n"

    return Response(m3u_content, mimetype='audio/x-mpegurl') [cite: 154]

if __name__ == '__main__':
    # Puerto para Render [cite: 156]
    app.run(host='0.0.0.0', port=10000)
