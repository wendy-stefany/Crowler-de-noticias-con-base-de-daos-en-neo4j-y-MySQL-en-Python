import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ConexionMySql import ConexionMySQL
from ConexionNeo4j import ConexionNeo4j


url = 'https://www.eluniversal.com.mx/minuto-x-minuto/todos/'
periodico_nombre = 'El universal'
fecha_referencia = datetime(2024, 5, 1)

class ElUniversal:

    def convertirFecha(self,string_fecha):
        # Expresión regular para encontrar la fecha y la hora
        regex = r"\|\s*(\d{2}/\d{2}/\d{4})\s*\|\s*(\d{2}:\d{2})\s*\|"

        # Buscar coincidencias en el string
        match = re.search(regex, string_fecha)

        if match:
            # Obtener la fecha y la hora encontradas
            fecha_str = match.group(1)
            hora_str = match.group(2)

            # Formatear la fecha y la hora en un objeto datetime
            fecha_hora = datetime.strptime(fecha_str + " " + hora_str, "%d/%m/%Y %H:%M")

            return fecha_hora
        
        return False
    
    def obtenerNoticiaCompleta(url_noticia, titulo):
        try:
            url_noticia_completa = 'https://www.eluniversal.com.mx' + str(url_noticia)
            page = requests.get(url_noticia_completa)

            if page.status_code == 200:
                html_noticia = BeautifulSoup(page.text, 'html.parser')
                noticia = html_noticia.find('div', { 'class':'encabezado ml-2.5 mr-2.5' })
                
                string_fecha = noticia.find('span', { 'class':'sc__author--date text-sm p-1 md:float-left flex'}).getText()
                fecha = ElUniversal().convertirFecha(string_fecha)
                autor = noticia.find('div', { 'class':'sc__author-nota font-bold text-lg'}).getText()
                resumen = noticia.find('h2',{'subTitle text-2xl mb-5'}).getText()

                if fecha >= fecha_referencia:
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
            url_temporal = url + str(i)
            page = requests.get(url_temporal)

            if page.status_code == 200:
                html = BeautifulSoup(page.text, 'html.parser')
                noticias = html.find_all('article', { 'class':'story-item md:flex md:pb-4 pt-5 border-b w-full' })

                for j, noticia in enumerate(noticias):
                    titulo = noticia.find('h2',{ 'class': 'minuto-x-minuto__title font-medium text-2xl'}).find('a').getText()
                    url_not = noticia.find('a', {'class' : 'cardsMXM pb-1'})
                    url_noticia = url_not['href']

                    noticia = ElUniversal.obtenerNoticiaCompleta(url_noticia,titulo)
                    if noticia == "Noticias obtenidas":
                        break
            if noticia == "Noticias obtenidas":
                print("Obtención finalizada")
                break
                    