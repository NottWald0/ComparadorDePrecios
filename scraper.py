# Importamos las herramientas que necesitamos
from selenium import webdriver  # Para abrir y controlar un navegador
from selenium.webdriver.chrome.service import Service  # Para usar ChromeDriver
from selenium.webdriver.common.by import By  # Para buscar cosas en la página web
import json  # Para trabajar con archivos JSON
import time  # Para hacer pausas
import threading  # Para usar varios hilos y hacer todo más rápido
from queue import Queue  # Para organizar las tareas de los hilos

# Esta función extrae los datos de un restaurante específico
def scrape_restaurant(restaurante, resultados, lock):
    # Mostramos qué restaurante estamos procesando y en qué hilo
    print(f"Extrayendo datos de {restaurante['nombre']} en hilo {threading.current_thread().name}...")

    # Configuramos el navegador Chrome para este hilo
    servicio = Service(executable_path="C:/Users/danib/ComparadorDePrecios/chromedriver.exe")
    navegador = webdriver.Chrome(service=servicio)

    # Abrimos la página del restaurante usando su enlace
    enlace = restaurante["enlace"]
    navegador.get(enlace)
    time.sleep(10)  # Esperamos 10 segundos para que la página cargue bien

    # Creamos un diccionario para guardar los datos del restaurante
    datos_restaurante = {
        "nombre": restaurante["nombre"],  # Nombre del restaurante
        "plataforma": "Uber Eats",        # Plataforma de donde sacamos los datos
        "direccion": restaurante["direccion"],  # Dirección del restaurante
        "productos": []                   # Lista vacía para los productos
    }

    try:
        # Buscamos todos los elementos <li> que tienen la info de los productos
        elementos = navegador.find_elements(By.TAG_NAME, "li")

        # Recorremos cada elemento para sacar nombre y precio
        for elemento in elementos:
            try:
                # Buscamos las etiquetas <span> que tienen el texto que nos interesa
                etiquetas = elemento.find_elements(By.CSS_SELECTOR, "span[data-testid='rich-text']")
                nombre_producto = None  # Aquí guardaremos el nombre
                precio_producto = None  # Aquí guardaremos el precio

                # Revisamos cada etiqueta para encontrar nombre y precio
                for etiqueta in etiquetas:
                    texto = etiqueta.text.strip()  # Quitamos espacios extras
                    if "€" in texto:  # Si tiene "€", es el precio
                        precio_producto = float(texto.replace("€", "").replace(",", ".").strip())
                    elif texto and not precio_producto:  # Si no es precio, asumimos que es el nombre
                        nombre_producto = texto

                # Si encontramos nombre y precio, los guardamos
                if nombre_producto and precio_producto:
                    datos_restaurante["productos"].append({
                        "nombre": nombre_producto,          # Nombre del producto
                        "precio": precio_producto,          # Precio del producto
                        "fecha": time.strftime("%Y-%m-%d %H:%M:%S")  # Fecha y hora actual
                    })

            except Exception as e:
                # Si algo falla con un producto, mostramos el error
                print(f"Error al procesar un producto en {restaurante['nombre']}: {e}")

    except Exception as e:
        # Si falla encontrar los productos, mostramos el error
        print(f"Error al encontrar productos en {restaurante['nombre']}: {e}")

    # Cerramos el navegador para no dejarlo abierto
    navegador.quit()

    # Guardamos los datos en la lista de resultados usando un candado para evitar problemas entre hilos
    with lock:
        resultados.append(datos_restaurante)

# Esta función controla lo que hace cada hilo
def worker(queue, resultados, lock):
    while True:
        # Tomamos un restaurante de la cola
        restaurante = queue.get()
        if restaurante is None:  # Si no hay más restaurantes, terminamos
            queue.put(None)      # Ponemos la señal de fin para otros hilos
            break
        # Extraemos los datos del restaurante
        scrape_restaurant(restaurante, resultados, lock)
        queue.task_done()  # Marcamos la tarea como terminada

# Lista de restaurantes con sus enlaces, nombres y direcciones
lista_restaurantes = [
    {
        "enlace": "https://www.ubereats.com/es/store/mcdonalds-carabanchel/lGfE3RJeSEGrw2Vi2Cxa4Q?ad_id=739716807100&campaign_id=10947348928&chain_slug=mcdonalds&diningMode=DELIVERY&gclid=Cj0KCQjw2N2_BhCAARIsAK4pEkU5TjLktt_XLVSKHvt24kMXhYsHxxRIy71sS-pMSY_-9jMzP7F4SDEaAnEyEALw_wcB&gclsrc=aw.ds&kw=&kwid=dsa-2473956379397&placement=&utm_campaign=CM2052283-search-google-nonbrand_162_-99_ES-National_e_all_acq_cpc_es-ES_DSA_Exact__dsa-2473956379397_739716807100_176004706265__m&utm_source=AdWords_NonBrand",
        "nombre": "McDonald's Carabanchel",
        "direccion": "Carabanchel, Madrid"
    },
    {
        "enlace": "https://www.ubereats.com/es/store/mcdonalds-plaza-castilla/9WdL8YvJRo2HHbk-GhxKGA?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkMlMkYlMjBkZSUyMFZpbGxhdmljaW9zYSUyQyUyMDQxJTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyQ2hJSm0tMVNJVy1JUVEwUnFjSkV5Yk9Ib1pBJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMmdvb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQwLjM5NjM2MTklMkMlMjJsb25naXR1ZGUlMjIlM0EtMy43NzE3NTkyJTdE",
        "nombre": "McDonald's Plaza Castilla",
        "direccion": "Plaza Castilla, Madrid"
    },
    {
        "enlace": "https://www.ubereats.com/es-en/store/mcdonalds-gran-via/sSnQZHiSQHKtKDW4tznf5Q?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkMlMkYlMjBkZSUyMFZpbGxhdmljaW9zYSUyQyUyMDQxJTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyQ2hJSm0tMVNJVy1JUVEwUnFjSkV5Yk9Ib1pBJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMmdvb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQwLjM5NjM2MTklMkMlMjJsb25naXR1ZGUlMjIlM0EtMy43NzE3NTkyJTdE&ps=1",
        "nombre": "McDonald's Gran Vía",
        "direccion": "Gran Vía, Madrid"
    },
    {
        "enlace": "https://www.ubereats.com/es-en/store/mcdonalds-la-paz/I2RHAAdRQgKubk50I5xZ5w?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkMlMkYlMjBkZSUyMFZpbGxhdmljaW9zYSUyQyUyMDQxJTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyQ2hJSm0tMVNJVy1JUVEwUnFjSkV5Yk9Ib1pBJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMmdvb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQwLjM5NjM2MTklMkMlMjJsb25naXR1ZGUlMjIlM0EtMy43NzE3NTkyJTdE",
        "nombre": "McDonald's La Paz",
        "direccion": "La Paz, Madrid"
    },
    {
        "enlace": "https://www.ubereats.com/es-en/store/mcdonalds-ventisquero-de-la-condesa/kM3l1cnyRw6WIENL270teQ?diningMode=DELIVERY&mod=merchantUnavailable&modctx=%257B%2522storeUuid%2522%253A%252290cde5d5-c9f2-470e-9620-434bdbbd2d79%2522%257D&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkMlMkYlMjBkZSUyMFZpbGxhdmljaW9zYSUyQyUyMDQxJTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyQ2hJSm0tMVNJVy1JUVEwUnFjSkV5Yk9Ib1pBJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMgdvdb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQwLjM5NjM2MTklMkMlMjJsb25naXR1ZGUlMjIlM0EtMy43NzE3NTkyJTdE&ps=1",
        "nombre": "McDonald's Ventisquero de la Condesa",
        "direccion": "Ventisquero de la Condesa, Madrid"
    },
    {
        "enlace": "https://www.ubereats.com/es-en/store/mcdonalds-montera/Wj22ufhhSHOzvFpLVsb_HA?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkMlMkYlMjBkZSUyMFZpbGxhdmljaW9zYSUyQyUyMDQxJTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyQ2hJSm0tMVNJVy1JUVEwUnFjSkV5Yk9Ib1pBJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMgdvdb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQwLjM5NjM2MTklMkMlMjJsb25naXR1ZGUlMjIlM0EtMy43NzE3NTkyJTdE&ps=1",
        "nombre": "McDonald's Montera",
        "direccion": "Montera, Madrid"
    },
    {
        "enlace": "https://www.ubereats.com/es-en/store/mcdonalds-goya/MEDEMv39QYmvpCCUgYjpBg?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkMlMkYlMjBkZSUyMFZpbGxhdmljaW9zYSUyQyUyMDQxJTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyQ2hJSm0tMVNJVy1JUVEwUnFjSkV5Yk9Ib1pBJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMgdvdb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQwLjM5NjM2MTklMkMlMjJsb25naXR1ZGUlMjIlM0EtMy43NzE3NTkyJTdE",
        "nombre": "McDonald's Goya",
        "direccion": "Goya, Madrid"
    },
    {
        "enlace": "https://www.ubereats.com/es-en/store/mcdonalds-la-gavia/tdEv_CyUQweP8Sx6hRbThA?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkMlMkYlMjBkZSUyMFZpbGxhdmljaW9zYSUyQyUyMDQxJTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyQ2hJSm0tMVNJVy1JUVEwUnFjSkV5Yk9Ib1pBJTIyJTJDJTIycmVmZXJlnmNlVHlwZSUyMiUzQSUyMgdvdb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQwLjM5NjM2MTklMkMlMjJsb25naXR1ZGUlMjIlM0EtMy43NzE3NTkyJTdE&ps=1",
        "nombre": "McDonald's La Gavia",
        "direccion": "La Gavia, Madrid"
    },
    {
        "enlace": "https://www.ubereats.com/es/store/mcdonalds-atocha/JTpFmDbKSti7q8iD6AlqbQ?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkMlMkYlMjBkZSUyMFZpbGxhdmljaW9zYSUyQyUyMDQxJTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyQ2hJSm0tMVNJVy1JUVEwUnFjSkV5Yk9Ib1pBJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMgdvdb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQwLjM5NjM2MTklMkMlMjJsb25naXR1ZGUlMjIlM0EtMy43NzE3NTkyJTdE&ps=1",
        "nombre": "McDonald's Atocha",
        "direccion": "Atocha, Madrid"
    },
    {
        "enlace": "https://www.ubereats.com/es/store/mcdonalds-vallecas-villa/GFoBbofnSSmXHizBQ0QIpA?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkMlMkYlMjBkZSUyMFZpbGxhdmljaW9zYSUyQyUyMDQxJTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyQ2hJSm0tMVNJVy1JUVEwUnFjSkV5Yk9Ib1pBJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMgdvdb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQwLjM5NjM2MTklMkMlMjJsb25naXR1ZGUlMjIlM0Et3.7717592%7D",
        "nombre": "McDonald's Vallecas Villa",
        "direccion": "Vallecas Villa, Madrid"
    }
]

# Estructura del JSON para guardar los datos
informacion = {
    "restaurantes": []
}

# Configuramos el sistema de hilos
NUM_THREADS = 3  # Usaremos 3 hilos para trabajar al mismo tiempo
queue = Queue()  # Cola para repartir los restaurantes entre los hilos
resultados = []  # Lista donde guardaremos los datos de todos los restaurantes
lock = threading.Lock()  # Candado para que los hilos no se pisen al guardar datos

# Ponemos todos los restaurantes en la cola
for restaurante in lista_restaurantes:
    queue.put(restaurante)

# Añadimos una señal para que los hilos sepan cuándo terminar
queue.put(None)

# Creamos y encendemos los hilos
threads = []
for i in range(NUM_THREADS):
    # Creamos un hilo que usa la función worker
    t = threading.Thread(target=worker, args=(queue, resultados, lock), name=f"Hilo-{i+1}")
    t.start()  # Lo encendemos
    threads.append(t)  # Lo guardamos en una lista

# Esperamos a que todos los hilos terminen
for t in threads:
    t.join()

# Guardamos todos los resultados en el diccionario
informacion["restaurantes"] = resultados

# Escribimos los datos en un archivo JSON
with open("datos_extraidos.json", "w", encoding="utf-8") as archivo:
    json.dump(informacion, archivo, ensure_ascii=False, indent=4)  # Guardamos con formato legible

# Avisamos que terminamos
print("Extracción completada. Datos guardados en datos_extraidos.json")