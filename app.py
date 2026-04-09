import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, Response

app = Flask(__name__)

@app.route('/lista.m3u')
def generar_m3u():
    # Usamos la URL principal en lugar del sitemap por si hay bloqueos de SEO
    url_fuente = "https://www.peelink2.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # 1. Obtenemos la página principal para sacar las últimas películas
        r = requests.get(url_fuente, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        # Buscamos todos los enlaces que parezcan películas (ajustado a la estructura de la web)
        enlaces = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Filtramos para que sean links de películas y no categorías o avisos legales
            if '/202' in href and '.html' in href and href not in enlaces:
                enlaces.append(href)
        
        # Tomamos las 15 más recientes
        entradas = enlaces[:15]
    except Exception as e:
        return f"Error conectando: {e}", 500

    m3u_content = "#EXTM3U\n\n"
    
    for url_pelicula in entradas:
        try:
            res = requests.get(url_pelicula, headers=headers, timeout=5)
            # Buscamos el link de vimeos.net
            match = re.search(r'https?://vimeos\.net/embed/[\w-]+', res.text)
            
            if match:
                video_link = match.group(0)
                # Extraemos un título limpio
                titulo = url_pelicula.split('/')[-1].replace('.html', '').replace('-', ' ').title()
                
                m3u_content += f'#EXTINF:-1, {titulo}\n'
                m3u_content += f"{video_link}\n\n"
        except:
            continue

    # Si después de todo sigue vacía, añadimos un canal de prueba para saber que el script corre
    if m3u_content == "#EXTM3U\n\n":
        m3u_content += "#EXTINF:-1, Servidor Activo - Sin peliculas encontradas hoy\n"
        m3u_content += "https://vimeos.net/embed/null\n"

    return Response(m3u_content, mimetype='audio/x-mpegurl')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
