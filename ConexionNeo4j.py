from neo4j import GraphDatabase

class ConexionNeo4j:
    def __init__(self):
        uri = "neo4j+s://2b470d0a.databases.neo4j.io"
        usuario = "neo4j"
        contraseña = "tCP1PdHtgnr2PF7UZAOPu8sKfiobDgzQvYckwZAwpyE"

        self._driver = GraphDatabase.driver(uri, auth=(usuario, contraseña))

    def close(self):
        self._driver.close()

    def insertar_noticia(self, periodico, autor, titulo, url, resumen, fecha):
        with self._driver.session() as session:
            query = (
                    "MERGE (p:Periodico {periodico: $periodico}) "
                    "MERGE (a:Autor {autor: $autor}) "
                    "CREATE (n:Noticia { "
                    "    titulo: $titulo, "
                    "    url: $url, "
                    "    resumen: $resumen, "
                    "    fecha: $fecha "
                    "}) "
                    "MERGE (n)-[:PUBLICADO_EN]->(p) "
                    "MERGE (n)-[:ESCRITO_POR]->(a) "
                )
            session.run(query, periodico=periodico, autor=autor, titulo=titulo, url=url, resumen=resumen, fecha=fecha)
