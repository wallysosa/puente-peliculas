import re
import time
import logging
from flask import Flask, Response
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Configuración de logs para ver el progreso en la consola de Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cache en memoria para no saturar la RAM de 4GB ni el CPU de Render [cite: 57]
_cache = {'content': None, 'timestamp': 0}
CACHE_TTL = 3600  # Los resultados se guardan por 1 hora [cite: 58]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_movie_links():
    """Obtiene las URLs de las películas desde la portada [cite: 67]"""
    logger.info("Iniciando navegación en la portada...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(extra_http_headers=HEADERS)
        # Esperamos a que el sitio termine de cargar sus scripts [cite: 72]
        page.goto('https://www.peelink2.com/2025/12/ver-avatar-fuego-y-ceniza-2025-gratis.html', wait_until='networkidle', timeout=60000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    seen, links = set(), []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/'):
            href = 'https://www.peelink2.com' + href
        # Filtramos solo enlaces de películas posteados desde el 2020 [cite: 82]
        if '/202' in href and href.endswith('.html') and href not in seen:
            seen.add(href)
            links.append(href)
    return links[:10]  # Limitamos a 10 para ahorrar memoria en el plan Free [cite: 85]

def extract_stream_url(movie_url):
    """Entra a cada película y captura el tráfico de red [cite: 86]"""
    stream_url = None
    title = movie_url.split('/')[-1].replace('.html', '').replace('-', ' ').title()

    # Interceptor de red: si pasa un .m3u8 o vimeos.net, lo atrapamos [cite: 95, 96]
    def intercept(request):
        nonlocal stream_url
        if re.search(r'vimeos\.net/embed/|video\.m3u8', request.url) and not stream_url:
            stream_url = request.url
            logger.info(f"Stream capturado: {stream_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(extra_http_headers=HEADERS)
        page.on('request', intercept)
        try:
            # Damos tiempo al reproductor para que cargue [cite: 105, 106]
            page.goto(movie_url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(5000) 
        except Exception as e:
            logger.warning(f"Timeout o error en {title}: {e}")
        finally:
            browser.close()
    return stream_url, title

def build_m3u():
    """Genera el texto final del archivo M3U [cite: 124]"""
    lines = ['#EXTM3U', '']
    try:
        movie_links = get_movie_links()
    except Exception as e:
        logger.error(f"Error en sitemap: {e}")
        return '#EXTM3U\n#EXTINF:-1, Error de conexion\nhttps://vimeos.net/null\n'

    for url in movie_links:
        try:
            stream, title = extract_stream_url(url)
            if stream:
                lines.append(f'#EXTINF:-1, {title}')
                lines.append(stream)
                lines.append('')
        except Exception as e:
            continue
    
    if len(lines) <= 2:
        return '#EXTM3U\n#EXTINF:-1, Sin contenido encontrado\nhttps://vimeos.net/null\n'
    
    return '\n'.join(lines)

@app.route('/lista.m3u')
def generar_m3u():
    """Ruta principal que sirve la lista a tu JVC Smart TV [cite: 146]"""
    now = time.time()
    # Si tenemos una versión guardada hace menos de una hora, la servimos rápido [cite: 149]
    if _cache['content'] and (now - _cache['timestamp']) < CACHE_TTL:
        return Response(_cache['content'], mimetype='audio/x-mpegurl')
    
    content = build_m3u()
    _cache['content'] = content
    _cache['timestamp'] = now
    return Response(content, mimetype='audio/x-mpegurl')

if __name__ == '__main__':
    # Render usa el puerto 10000 por defecto [cite: 156]
    app.run(host='0.0.0.0', port=10000)
