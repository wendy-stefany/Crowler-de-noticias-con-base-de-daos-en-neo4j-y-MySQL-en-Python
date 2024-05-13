import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ConexionMySql import ConexionMySQL
from ConexionNeo4j import ConexionNeo4j

url = 'https://www.excelsior.com.mx/ultima-hora?page='
periodico_nombre = 'Excelsior'
fecha_referencia = datetime(2024, 5, 1)

headers = {
    'Host': 'www.excelsior.com.mx',
    'Sec-Ch-Ua': '" Not A;Brand";v="99", "Chromium";v="90"',
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
    'Connection': 'close'
}

class Excelsior:

    def convertirFecha(self,string_fecha):
        # Expresión regular para encontrar el patrón de fecha
        patron_fecha = r'\|\s*(\d{2}-\d{2}-\d{4})'  # Por ejemplo: | 10-05-2024
        patron_hora = r'\|\s*(\d{2}:\d{2})\s+hrs\.'  # Por ejemplo: | 18:34 hrs.

        # Buscar coincidencias en la string_fecha
        match_fecha = re.search(patron_fecha, string_fecha)
        match_hora = re.search(patron_hora, string_fecha)

        if match_fecha:
            # Si se encuentra el patrón de fecha, extraer la fecha y convertirla a datetime
            fecha_str = match_fecha.group(1)
            fecha_datetime = datetime.strptime(fecha_str, "%d-%m-%Y")
            return fecha_datetime

        elif match_hora:
            # Si se encuentra el patrón de hora, obtener la hora y minutos y agregarla a la fecha actual
            hora_str = match_hora.group(1)
            hora_datetime = datetime.now().replace(hour=int(hora_str[:2]), minute=int(hora_str[3:]))
            return hora_datetime

        else:
            # Si no se encuentra ninguno de los patrones, retornar None
            return None
        
    def convertirAutor(self,string_autor):
        # Patrón para buscar antes de '/' o '|'
        patron = r'([^/|\n]+)'
        # Buscar coincidencias en la cadena
        coincidencias = re.findall(patron, string_autor)
        # El primer elemento de la lista es el nombre que queremos extraer
        if coincidencias:
            return coincidencias[0]
        else:
            return None


    def obtenerNoticiaCompleta(url_noticia):
        try:
            page = requests.get(url_noticia, headers=headers)
            url = url_noticia.split('/')
            
            if page.status_code == 200:
                html_noticia = BeautifulSoup(page.text, 'html.parser')
                
                noticia = html_noticia.find('div', { 'class':'encabezado ml-2.5 mr-2.5' })
                
                titulo = html_noticia.find('h1', { 'class':'title'}).getText()
                resumen = html_noticia.find('h2', { 'class':'teaser' }).getText()
                autor = html_noticia.find('span', { 'class':'author-name' }).getText()
                fecha = html_noticia.find('span', { 'class':'hour' }).getText()
                
                fecha = Excelsior().convertirFecha(fecha)
                autor = Excelsior().convertirAutor(autor)

                if fecha >= fecha_referencia:
                    # Consultas a base de datos mysql
                    periodico_id = ConexionMySQL().obtener_periodico(periodico_nombre)
                    autor_id = ConexionMySQL().obtener_autor(autor)

                    # Inserta a base de datos relacional
                    ConexionMySQL().insertar_noticia(periodico_id, autor_id, titulo, url_noticia, resumen, fecha)

                    # Inserta a base de datos NO relaciona No4j
                    ConexionNeo4j().insertar_noticia(periodico_nombre, autor, titulo, url_noticia, resumen, fecha)
                else:
                    return "Noticias obtenidas"
        except:
            return False

    def obtenerNoticias(self):
        print("Obteniendo noticias del periodico " + periodico_nombre + " ...")
        i = 0
        while True:
            i += 1
            url_temporal = url + str(i)
            page = requests.get(url_temporal, headers=headers)

            if page.status_code == 200:
                html = BeautifulSoup(page.text, 'html.parser')
                noticias = html.find_all('li', { 'class':'item-media' })
                # print(noticias)
                for j, noticia in enumerate(noticias):
                    link = noticia.find('a', {'class' : 'media'})
                    url_noticia = link['href']

                    noticia = Excelsior.obtenerNoticiaCompleta(url_noticia)
                    if noticia == "Noticias obtenidas":
                        break
            if noticia == "Noticias obtenidas":
                print("Obtención finalizada")
                break