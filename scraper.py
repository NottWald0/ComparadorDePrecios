# scraper.py
from selenium import webdriver  # Para abrir y controlar un navegador
from selenium.webdriver.chrome.service import Service  # Para usar ChromeDriver
from selenium.webdriver.common.by import By  # Para buscar en la página web
import json  # Para trabajar con archivos JSON
import time  # Para pausas
import threading  # Para hilos
from queue import Queue  # Para cola de tareas

# Carga la lista de restaurantes desde un archivo externo
with open('lista_restaurantes.json', 'r', encoding='utf-8') as f:
    lista_restaurantes = json.load(f)

# Función que extrae datos de un restaurante
def scrape_restaurant(restaurante, resultados, lock):
    print(f"Extrayendo datos de {restaurante['nombre']} en hilo {threading.current_thread().name}...")
    servicio = Service(executable_path="C:/Users/danib/ComparadorDePrecios/chromedriver.exe")
    navegador = webdriver.Chrome(service=servicio)
    navegador.get(restaurante["enlace"])
    time.sleep(10)

    datos = {
        "nombre": restaurante["nombre"],
        "plataforma": restaurante.get("plataforma", "Uber Eats"),
        "direccion": restaurante.get("direccion", ""),
        "productos": []
    }

    try:
        items = navegador.find_elements(By.TAG_NAME, "li")
        for item in items:
            nombre = None
            precio = None
            spans = item.find_elements(By.CSS_SELECTOR, "span[data-testid='rich-text']")
            for span in spans:
                text = span.text.strip()
                if '€' in text:
                    try:
                        precio = float(text.replace('€','').replace(',','.').strip())
                    except:
                        precio = None
                elif text and not precio:
                    nombre = text
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

    with lock:
        resultados.append(datos)

# Worker para hilos
def worker(queue, resultados, lock):
    while True:
        restaurante = queue.get()
        if restaurante is None:
            queue.put(None)
            break
        scrape_restaurant(restaurante, resultados, lock)
        queue.task_done()

if __name__ == '__main__':
    resultados = []
    lock = threading.Lock()
    queue = Queue()
    NUM_THREADS = 3

    # Carga restaurantes en la cola
    for r in lista_restaurantes:
        queue.put(r)
    queue.put(None)

    # Inicia hilos
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=worker, args=(queue, resultados, lock), name=f"Hilo-{i+1}")
        t.start()
        threads.append(t)

    # Espera finalización
    for t in threads:
        t.join()

    # Guarda resultados
    datos_final = {"restaurantes": resultados}
    with open('datos_extraidos.json', 'w', encoding='utf-8') as out:
        json.dump(datos_final, out, ensure_ascii=False, indent=4)

    print("Extracción completada. Datos guardados en datos_extraidos.json")
