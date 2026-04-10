import os
import re
import logging
from flask import Flask, Response
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def extraer_link_seguro():
    url_pelicula = "https://www.peelink2.com/2025/12/ver-avatar-fuego-y-ceniza-2025-gratis.html"
    stream_url = None

    # Iniciamos Playwright con máximo ahorro de energía
    with sync_playwright() as p:
        # Argumentos cruciales para servidores pequeños
        browser = p.chromium.launch(
            headless=True, 
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage", 
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--single-process" # Ayuda a que no se dispare el uso de RAM
            ]
        )
        
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()

        # Bloqueamos imágenes y fuentes para ahorrar RAM
        page.route("**/*.{png,jpg,jpeg,svg,woff,woff2,css}", lambda route: route.abort())

        def interceptar(request):
            nonlocal stream_url
            # El patrón que encontraste antes
            if ".m3u8" in request.url and not stream_url:
                stream_url = request.url
                logger.info(f"Stream capturado con éxito")

        page.on("request", interceptar)

        try:
            # Vamos directo al grano, sin esperar a que cargue toda la basura de la web
            page.goto(url_pelicula, wait_until="commit", timeout=45000)
            # Esperamos lo justo para que el reproductor suelte el link
            page.wait_for_timeout(8000)
        except Exception as e:
            logger.error(f"Error de carga: {e}")
        finally:
            context.close()
            browser.close()

    return stream_url

@app.route('/lista.m3u')
def generar_m3u():
    url_final = extraer_link_seguro()
    
    m3u = "#EXTM3U\n"
    if url_final:
        m3u += "#EXTINF:-1, Avatar: Fuego y Ceniza (HLS)\n"
        m3u += f"{url_final}\n"
    else:
        m3u += "#EXTINF:-1, [Reintentar] No se capturo el stream\n"
        m3u += "https://vimeos.net/null\n"
        
    return Response(m3u, mimetype='audio/x-mpegurl')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
