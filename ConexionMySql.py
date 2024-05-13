import mysql.connector

class ConexionMySQL:
    def __init__(self):
        self.host = "127.0.0.1"
        self.usuario = "root"
        self.contraseña = ""
        self.base_datos = "periodicos"
        self.conexion = None

        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                user=self.usuario,
                password=self.contraseña,
                database=self.base_datos
            )
        except mysql.connector.Error as err:
            print("Error al conectar a la base de datos:", err)


    def obtener_periodico(self, nombre_periodico):
        # Consultar existencia el periodico
        consulta = "SELECT id FROM periodicos WHERE periodico = %s"
        consultar = self.conexion.cursor(dictionary=True)
        consultar.execute(consulta, (nombre_periodico,))
        periodico =  consultar.fetchall()  

        # Si el periodico existe retorna id si no lo crea y retorna id
        if(periodico):
            for fila in periodico:
                periodico_id = fila['id']
                return periodico_id  
        else:
            # Crea registro de nuevo autor
            consulta = "INSERT INTO periodicos (periodico) VALUES (%s)"
            insertar = self.conexion.cursor(dictionary=True)
            insertar.execute(consulta, (nombre_periodico,))
            self.conexion.commit()

            autor = self.obtener_periodico(nombre_periodico)
            return autor
        

    def obtener_autor(self, nombre_autor):
        
        # Consultar existencia se autor
        consulta = "SELECT id FROM autores WHERE autor = %s"
        consultar = self.conexion.cursor(dictionary=True)
        consultar.execute(consulta, (nombre_autor,))
        autor =  consultar.fetchall() 

        # Si el autor existe retorna id si no lo crea y retorna id
        if(autor):
            for fila in autor:
                autor_id = fila['id']
                return autor_id
        else:
            # Crea registro de nuevo autor
            consulta = "INSERT INTO autores (autor) VALUES (%s)"
            insertar = self.conexion.cursor(dictionary=True)
            insertar.execute(consulta, (nombre_autor,))
            self.conexion.commit()

            autor = self.obtener_autor(nombre_autor)
            return autor
            
                
    def insertar_noticia(self, periodico, autor, titulo, url, resumen, fecha):
        consulta = "INSERT INTO noticias (`periodico_id`, `autor_id`, `titulo`, `url`, `resumen`, `fecha`) VALUES (%s, %s, %s, %s, %s, %s)"

        insertar = self.conexion.cursor(dictionary=True)
        insertar.execute(consulta, (periodico, autor, titulo, url, resumen, fecha))
        self.conexion.commit()

    def ejecutar(self, command):
        cursor = self.conexion.cursor()
        cursor.execute(command)
        self.conexion.commit()
        return True

    def cerrar_conexion(self):
        if self.conexion.is_connected():
            self.conexion.close()
