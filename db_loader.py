import json
import pymysql
from datetime import datetime

# Conexión a MySQL
connection = pymysql.connect(
    host="localhost",
    user="root",  # Cambia por tu usuario si no es root
    password="root",  # Cambia por tu contraseña de MySQL
    database="comparador_de_precios"
)
cursor = connection.cursor()

# Lee el JSON
with open("scraped_data.json", "r", encoding="utf-8") as file:
    datos = json.load(file)

# Procesa cada restaurante
for restaurante in datos["restaurantes"]:
    # Inserta o verifica el restaurante
    cursor.execute("SELECT id_restaurante FROM Restaurante WHERE nombre = %s", (restaurante["nombre"],))
    result = cursor.fetchone()
    if result:
        id_restaurante = result[0]
    else:
        cursor.execute("INSERT INTO Restaurante (nombre) VALUES (%s)", (restaurante["nombre"],))
        id_restaurante = cursor.lastrowid

    # Procesa los productos del restaurante
    for producto in restaurante["productos"]:
        # Inserta o verifica el producto
        cursor.execute("SELECT id_producto FROM Productos WHERE nombre = %s AND id_restaurante = %s",
                       (producto["nombre"], id_restaurante))
        result = cursor.fetchone()
        if result:
            id_producto = result[0]
        else:
            cursor.execute("INSERT INTO Productos (nombre, id_restaurante) VALUES (%s, %s)",
                           (producto["nombre"], id_restaurante))
            id_producto = cursor.lastrowid

        # Convierte la fecha del JSON a formato DATETIME
        fecha = datetime.strptime(producto["fecha"], "%Y-%m-%d %H:%M:%S")

        # Verifica si el producto ya tiene un precio actual
        cursor.execute("SELECT id_precio, precio, fecha FROM Precio WHERE id_producto = %s", (id_producto,))
        precio_actual = cursor.fetchone()

        if precio_actual:
            # Si el precio cambió, guarda el precio anterior en Historico y actualiza Precio
            if precio_actual[1] != producto["precio"]:
                cursor.execute("INSERT INTO Historico (id_producto, precio, fecha) VALUES (%s, %s, %s)",
                               (id_producto, precio_actual[1], precio_actual[2]))
                cursor.execute("UPDATE Precio SET precio = %s, fecha = %s WHERE id_producto = %s",
                               (producto["precio"], fecha, id_producto))
        else:
            # Si no hay precio, inserta uno nuevo
            cursor.execute("INSERT INTO Precio (id_producto, precio, fecha) VALUES (%s, %s, %s)",
                           (id_producto, producto["precio"], fecha))

# Guarda los cambios
connection.commit()
connection.close()

print("Datos volcados a la base de datos correctamente.")