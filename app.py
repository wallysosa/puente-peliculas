import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, Response

app = Flask(__name__)

@app.route('/lista.m3u')
def generar_m3u():
    sitemap_url = "https://www.peelink2.com/post-sitemap.xml"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        r = requests.get(sitemap_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'xml')
        # Tomamos solo las últimas 15 entradas para que la TV no espere demasiado
        entradas = soup.find_all('url')[:15]
    except Exception as e:
        return f"Error conectando al catálogo: {e}", 500

    # Cabecera M3U
    m3u_content = "#EXTM3U\n\n"
    
    for entrada in entradas:
        try:
            url_pelicula = entrada.find('loc').text
            
            # Intentar extraer la imagen del sitemap
            imagen_tag = entrada.find('image:loc')
            url_imagen = imagen_tag.text if imagen_tag else ""
            
            # Buscar el enlace del reproductor
            res = requests.get(url_pelicula, headers=headers, timeout=5)
            match = re.search(r'https?://vimeos\.net/embed/[\w-]+', res.text)
            
            if match:
                video_link = match.group(0)
                # Limpiar el título
                titulo = url_pelicula.split('/')[-2].replace('-', ' ').title()
                
                # Escribir la estructura M3U con imagen
                m3u_content += f'#EXTINF:-1 tvg-logo="{url_imagen}", {titulo}\n'
                m3u_content += f"{video_link}\n\n"
        except:
            continue

    # Devolvemos el texto como un archivo de lista de reproducción
    return Response(m3u_content, mimetype='audio/x-mpegurl')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)