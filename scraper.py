from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
import time

# Configura Selenium con ChromeDriver
service = Service(executable_path="C:/Users/danib/ComparadorDePrecios/chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Lista de restaurantes a scrapear
restaurantes = [
    {
        "url": "https://www.ubereats.com/es/store/mcdonalds-carabanchel/lGfE3RJeSEGrw2Vi2Cxa4Q?ad_id=739716807100&campaign_id=10947348928&chain_slug=mcdonalds&diningMode=DELIVERY&gclid=Cj0KCQjw2N2_BhCAARIsAK4pEkU5TjLktt_XLVSKHvt24kMXhYsHxxRIy71sS-pMSY_-9jMzP7F4SDEaAnEyEALw_wcB&gclsrc=aw.ds&kw=&kwid=dsa-2473956379397&placement=&utm_campaign=CM2052283-search-google-nonbrand_162_-99_ES-National_e_all_acq_cpc_es-ES_DSA_Exact__dsa-2473956379397_739716807100_176004706265__m&utm_source=AdWords_NonBrand",
        "nombre": "McDonald's Carabanchel",
        "direccion": "Carabanchel, Madrid"
    },
    {
        "url": "https://www.ubereats.com/es/store/mcdonalds-plaza-castilla/9WdL8YvJRo2HHbk-GhxKGA?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkMlMkYlMjBkZSUyMFZpbGxhdmljaW9zYSUyQyUyMDQxJTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyQ2hJSm0tMVNJVy1JUVEwUnFjSkV5Yk9Ib1pBJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMmdvb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQwLjM5NjM2MTklMkMlMjJsb25naXR1ZGUlMjIlM0EtMy43NzE3NTkyJTdE",
        "nombre": "McDonald's Plaza Castilla",
        "direccion": "Plaza Castilla, Madrid"
    }
]

# Estructura del JSON
datos = {
    "restaurantes": []
}

# Scraping de cada restaurante
for restaurante in restaurantes:
    print(f"Scraping {restaurante['nombre']}...")
    driver.get(restaurante["url"])
    time.sleep(5)  # Espera a que cargue la página

    restaurante_datos = {
        "nombre": restaurante["nombre"],
        "plataforma": "Uber Eats",
        "direccion": restaurante["direccion"],
        "productos": []
    }

    try:
        # Encuentra contenedores de productos (ajústalo según la estructura)
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
                    restaurante_datos["productos"].append({
                        "nombre": nombre,
                        "precio": precio,
                        "fecha": time.strftime("%Y-%m-%d %H:%M:%S")
                    })

            except Exception as e:
                print(f"Error al procesar un producto en {restaurante['nombre']}: {e}")
    except Exception as e:
        print(f"Error al encontrar productos en {restaurante['nombre']}: {e}")

    datos["restaurantes"].append(restaurante_datos)

# Guarda en JSON
with open("scraped_data.json", "w", encoding="utf-8") as file:
    json.dump(datos, file, ensure_ascii=False, indent=4)

# Cierra el navegador
driver.quit()

print("Scraping completado. Datos guardados en scraped_data.json")