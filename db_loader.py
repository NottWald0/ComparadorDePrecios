import json  
import pymysql  
from datetime import datetime 

# Configuro la conexión a MySQL
# Uso localhost porque la base de datos es local
conexion = pymysql.connect(
    host="localhost",
    user="root",  
    password="root",  
    database="comparador_de_precios"  
)
cursor = conexion.cursor()  # Creo un cursor para ejecutar consultas SQL


with open("datos_extraidos.json", "r", encoding="utf-8") as archivo:
    informacion = json.load(archivo)  # Primero leo el JSON y lo guardo en una variable

# -------------------Recorro cada restaurante del JSON para procesarlo-------------------------------------
for restaurante in informacion["restaurantes"]:
    # Compruebo si el restaurante ya esta en la base de datos
    cursor.execute("SELECT id_restaurante FROM Restaurante WHERE nombre = %s", (restaurante["nombre"],))
    resultado = cursor.fetchone()  

    # Si el restaurante ya existe, uso su ID; si no, lo inserto y uso su nuevo ID
    if resultado:
        id_restaurante = resultado[0]  # El ID del restaurante ya existente
    else:
        cursor.execute("INSERT INTO Restaurante (nombre) VALUES (%s)", (restaurante["nombre"],))  # Inserto el restaurante
        id_restaurante = cursor.lastrowid  # Obtengo el ID del restaurante  


    # ------------------------Ahora proceso los productos del restaurante---------------------------------------
    for producto in restaurante["productos"]:
        # Compruebo si el producto ya está en la base de datos para el restaurante
        cursor.execute("SELECT id_producto FROM Productos WHERE nombre = %s AND id_restaurante = %s",
                       (producto["nombre"], id_restaurante))
        resultado = cursor.fetchone() 

        if resultado:
            id_producto = resultado[0]  
        else:
            cursor.execute("INSERT INTO Productos (nombre, id_restaurante) VALUES (%s, %s)",
                           (producto["nombre"], id_restaurante))  
            id_producto = cursor.lastrowid  

        # ----------------A continuacion convierto la fecha del JSON a un formato que MySQL entienda-----------------
        fecha = datetime.strptime(producto["fecha"], "%Y-%m-%d %H:%M:%S")

        #--------------------- Finalmente compruebo si el producto ya tiene un precio registrado-----------------------------------
        cursor.execute("SELECT id_precio, precio, fecha FROM Precio WHERE id_producto = %s", (id_producto,))
        precio_actual = cursor.fetchone()  # Obtengo el precio actual, si existe

        # Si el producto ya tiene un precio registrado
        if precio_actual:
            # Comparo el precio actual con el nuevo precio del JSON
            if precio_actual[1] != producto["precio"]:  # Si el precio cambio guardo el precio anterior en la tabla Historico
                cursor.execute("INSERT INTO Historico (id_producto, precio, fecha) VALUES (%s, %s, %s)",
                               (id_producto, precio_actual[1], precio_actual[2]))
                # y actualizo el precio actual en la tabla Precio con el nuevo precio y fecha
                cursor.execute("UPDATE Precio SET precio = %s, fecha = %s WHERE id_producto = %s",
                               (producto["precio"], fecha, id_producto))
        else:
            # Si el producto no tiene precio, inserto un nuevo precio en la tabla Precio
            cursor.execute("INSERT INTO Precio (id_producto, precio, fecha) VALUES (%s, %s, %s)",
                           (id_producto, producto["precio"], fecha))

# Guardo todos los cambios en la base de datos
conexion.commit()
# Cierro la conexión a la base de datos para liberar recursos
conexion.close()


print("Datos cargados en la base de datos correctamente.")