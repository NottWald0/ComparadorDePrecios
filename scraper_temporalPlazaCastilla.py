from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
import time

# Configura Selenium con ChromeDriver
service = Service(executable_path="C:/Users/danib/ComparadorDePrecios/chromedriver.exe")
driver = webdriver.Chrome(service=service)

# URL de McDonald's Plaza Castilla
url = "https://www.ubereats.com/es/store/mcdonalds-plaza-castilla/9WdL8YvJRo2HHbk-GhxKGA?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkMlMkYlMjBkZSUyMFZpbGxhdmljaW9zYSUyQyUyMDQxJTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyQ2hJSm0tMVNJVy1JUVEwUnFjSkV5Yk9Ib1pBJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMmdvb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQwLjM5NjM2MTklMkMlMjJsb25naXR1ZGUlMjIlM0EtMy43NzE3NTkyJTdE"
driver.get(url)
time.sleep(5)  # Espera a que cargue la página

# Estructura del JSON
datos = {
    "restaurante": {
        "nombre": "McDonald's Plaza Castilla",
        "plataforma": "Uber Eats",
        "direccion": "Plaza Castilla, Madrid",  # Ajusta si encuentras la dirección exacta
        "productos": []
    }
}

# Busca los contenedores de productos
try:
    # Encuentra elementos que agrupan productos (ajústalo según la estructura real)
    items = driver.find_elements(By.TAG_NAME, "li")  # Podría ser <li>, <div>, etc.

    for item in items:
        try:
            # Busca nombre y precio dentro de cada contenedor
            spans = item.find_elements(By.CSS_SELECTOR, "span[data-testid='rich-text']")
            nombre = None
            precio = None

            for span in spans:
                texto = span.text.strip()
                if "€" in texto:  # Si tiene "€", es el precio
                    precio = float(texto.replace("€", "").replace(",", ".").strip())
                elif texto and not precio:  # Si no tiene "€" y no hemos encontrado precio, es el nombre
                    nombre = texto

            if nombre and precio:
                datos["restaurante"]["productos"].append({
                    "nombre": nombre,
                    "precio": precio,
                    "fecha": time.strftime("%Y-%m-%d %H:%M:%S")
                })

        except Exception as e:
            print(f"Error al procesar un producto: {e}")
except Exception as e:
    print(f"Error al encontrar productos: {e}")

# Guarda en JSON
with open("scraped_data.json", "w", encoding="utf-8") as file:
    json.dump(datos, file, ensure_ascii=False, indent=4)

# Cierra el navegador
driver.quit()

print("Scraping completado. Datos guardados en scraped_data.json")