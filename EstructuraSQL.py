from ConexionMySql import ConexionMySQL
from mysql.connector import Error

class EstructuraSql:

    periodicos = "CREATE TABLE IF NOT EXISTS periodicos (id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT, periodico VARCHAR(255)  NOT NULL)"
    autores = "CREATE TABLE IF NOT EXISTS autores (id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT, autor VARCHAR(255) NOT NULL)"
    noticias = "CREATE TABLE IF NOT EXISTS noticias (id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, periodico_id BIGINT UNSIGNED NOT NULL, autor_id BIGINT UNSIGNED NOT NULL, titulo VARCHAR(255) NOT NULL,url VARCHAR(255) NOT NULL, resumen TEXT NOT NULL, fecha DATETIME NOT NULL, CONSTRAINT noticias_autor_id_foreign FOREIGN KEY (autor_id) REFERENCES autores (id) ON DELETE CASCADE, CONSTRAINT noticias_periodico_id_foreign FOREIGN KEY (periodico_id) REFERENCES periodicos (id) ON DELETE CASCADE)"

    try:
        print("Creando tablas en MySql ...")
        ConexionMySQL().ejecutar(periodicos)
        ConexionMySQL().ejecutar(autores)
        ConexionMySQL().ejecutar(noticias)
        print("Creación finalizada.")
    except Error as error:
        print(error)
            