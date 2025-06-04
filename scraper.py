from selenium import webdriver                          
from selenium.webdriver.chrome.service import Service   
from selenium.webdriver.common.by import By             
import json                                              
import time                                              
import threading                                         
from queue import Queue                                  

# Cargo la lista de restaurantes desde un archivo JSON externo
with open('lista_restaurantes.json', 'r', encoding='utf-8') as f:
    lista_restaurantes = json.load(f)

# Función que extrae productos y precios de un restaurante
def scrape_restaurant(restaurante, resultados, lock):
    print(f"Extrayendo datos de {restaurante['nombre']} en hilo {threading.current_thread().name}...")

    # Configura el navegador Chrome
    servicio = Service(executable_path="C:/Users/danib/ComparadorDePrecios/chromedriver.exe")
    navegador = webdriver.Chrome(service=servicio)

    # Abre la página del restaurante
    navegador.get(restaurante["enlace"])
    time.sleep(10)  # Espera a que la página cargue para simular el comportamiento de un humano

    # Diccionario donde se guardarán los datos del restaurante
    datos = {
        "nombre": restaurante["nombre"],
        "plataforma": restaurante.get("plataforma", "Uber Eats"),
        "direccion": restaurante.get("direccion", ""),
        "productos": []  # Lista donde se guardarán los productos con precios
    }

    try:
        # Busca todos los elementos tipo <li> que podrían contener productos
        items = navegador.find_elements(By.TAG_NAME, "li")

        for item in items:
            nombre = None
            precio = None

            # Busco los spans que contengan texto dentro de la lista
            spans = item.find_elements(By.CSS_SELECTOR, "span[data-testid='rich-text']")

            for span in spans:
                text = span.text.strip()
                # Si contiene el simbolo '€', lo intento convertir a número
                if '€' in text:
                    try:
                        precio = float(text.replace('€','').replace(',','.').strip())
                    except:
                        precio = None
                # Si no es precio lo guardo como nombre
                elif text and not precio:
                    nombre = text

            # Cuando tengo precio y nombre los gyuardo en la lista
            if nombre and precio is not None:
                datos['productos'].append({
                    'nombre': nombre,
                    'precio': precio,
                    'fecha': time.strftime("%Y-%m-%d %H:%M:%S") 
                })

    except Exception as e:
        print(f"Error procesando productos en {restaurante['nombre']}: {e}")

    finally:
        navegador.quit()

    # Uso un lock para evitar problemas al modificar la lista compartida entre los hilos
    # Cuando un restaurante hilo este añadiendo info a la lista, los demas no pueden modificarla
    with lock:
        resultados.append(datos)

# Función que ejecuta la cola de restaurantes en hilos 
def worker(queue, resultados, lock):
    while True:
        restaurante = queue.get() # Cada vez que se llama a la cole, se recibe un restaurante para procesarlo y obtener la info
        if restaurante is None:
            queue.put(None) 
            break
        scrape_restaurant(restaurante, resultados, lock) #Si la funcion
        queue.task_done()  # Marca la tarea como terminada

# Punto de entrada del script
if __name__ == '__main__':
    resultados = []              
    lock = threading.Lock()      
    queue = Queue()              
    NUM_THREADS = 3              

    # Carga todos los restaurantes en la cola
    for r in lista_restaurantes:
        queue.put(r)
    queue.put(None)  

    # Crea y lanza los hilos
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=worker, args=(queue, resultados, lock), name=f"Hilo-{i+1}")
        t.start()
        threads.append(t)

    # Espera a que todos los hilos terminen
    for t in threads:
        t.join()

    # Guarda los resultados en un archivo JSON
    datos_final = {"restaurantes": resultados}
    with open('datos_extraidos.json', 'w', encoding='utf-8') as out:
        json.dump(datos_final, out, ensure_ascii=False, indent=4)

    print("Extracción completada. Datos guardados en datos_extraidos.json")
