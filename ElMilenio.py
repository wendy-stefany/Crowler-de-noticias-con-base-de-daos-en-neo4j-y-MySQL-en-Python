import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ConexionMySql import ConexionMySQL
from ConexionNeo4j import ConexionNeo4j

domain = "https://www.milenio.com"
url = "https://www.milenio.com/ultima-hora?page="
periodico_nombre = 'El Milenio'
fecha_referencia = datetime(2024, 5, 1)

headers = {
    'Host': 'www.milenio.com',
    'Sec-Ch-Ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Linux"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.60 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Priority': 'u=0, i',
    'Connection': 'open'
}

class ElMilenio:
    
    def convertirFecha(fecha_str):
        # Patrón para reconocer diferentes formatos de fecha
        patron = r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})|(\d{2})-(\d{2})-(\d{4}) (\d{2}):(\d{2}):(\d{2})'
        
        # Buscar coincidencias en la cadena de fecha
        match = re.match(patron, fecha_str)
        
        if match:
            # Extraer partes de la fecha
            if match.group(1):  # Formato 2024-05-12 17:43:00
                año, mes, dia, hora, minuto, segundo = match.groups()[:6]
            else:  # Formato 12-05-2024 17:56:50
                dia, mes, año, hora, minuto, segundo = match.groups()[6:]
            
            # Formatear la fecha y la hora en el formato deseado
            fecha_formateada = f"{año}-{mes}-{dia} {hora}:{minuto}:{segundo}"
            fecha_formateada = datetime.strptime(fecha_formateada, '%Y-%m-%d %H:%M:%S')

            return fecha_formateada
        else:
            return None
        
    def obtenerNoticiaCompleta(url_noticia):
        try:
            url = domain + url_noticia
            page = requests.get(url, headers=headers)
            
            if page.status_code == 200:
                page = BeautifulSoup(page.content, 'html.parser')
                
                titulo = page.find('h1', class_='nd-title-headline-title-headline-base__title')
                if not titulo:
                    titulo = page.find('h1', class_='nd-title-headline-title-headline-live__title').getText()
                else:
                    titulo = titulo.getText()
                
                resumen = page.find('h2', class_='nd-title-headline-title-headline-base__abstract').getText()

                string_fecha = page.find('div', class_='content-date').find('time')['datetime']
                fecha = ElMilenio.convertirFecha(string_fecha)
                
                if fecha >= fecha_referencia:
                    autor = page.find('span', class_='author').find('a')
                    if not autor:
                        autor = page.find('span', class_='author').getText()
                    else :
                        autor = autor.getText()
                        
                    autor = re.sub(r'[^\w\s,]', '', autor).strip()
                    autor = autor.split(',')[0]
                    
                    # Consultas a base de datos mysql
                    periodico_id = ConexionMySQL().obtener_periodico(periodico_nombre)
                    autor_id = ConexionMySQL().obtener_autor(autor)

                    # Inserta a base de datos relacional
                    ConexionMySQL().insertar_noticia(periodico_id, autor_id, titulo, url, resumen, fecha)

                    # Inserta a base de datos NO relaciona No4j
                    ConexionNeo4j().insertar_noticia(periodico_nombre, autor, titulo, url, resumen, fecha)
                else:
                    return "Noticias obtenidas"
        except:
            return False
        
    def obtenerNoticias(self):
        print("Obteniendo noticias del periodico " + periodico_nombre + " ...")
        i = 0
        while True:
            i += 1
            time.sleep(1)
            temp_url = url + str(i)
            page = requests.get(temp_url, headers=headers)
            
            if page.status_code == 200:
                page = BeautifulSoup(page.content, 'html.parser')
                
                noticias = page.find_all('li', class_='lr-list-row-row-news')
                
                for noticia in noticias:
                    url_noticia = noticia.find('a')['href']
                    
                    noticia = ElMilenio.obtenerNoticiaCompleta(url_noticia)
                    
                    if noticia == "Noticias obtenidas":
                        break
            if noticia == "Noticias obtenidas":
                print("Obtención finalizada")
                break
        