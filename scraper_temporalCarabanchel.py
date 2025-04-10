from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
import time

# Configura Selenium con ChromeDriver
service = Service(executable_path="C:/Users/danib/ComparadorDePrecios/chromedriver.exe")  # Ruta a chromedriver
driver = webdriver.Chrome(service=service)

# URL proporcionada
url = "https://www.ubereats.com/es/store/mcdonalds-carabanchel/lGfE3RJeSEGrw2Vi2Cxa4Q?ad_id=739716807100&campaign_id=10947348928&chain_slug=mcdonalds&diningMode=DELIVERY&gclid=Cj0KCQjw2N2_BhCAARIsAK4pEkU5TjLktt_XLVSKHvt24kMXhYsHxxRIy71sS-pMSY_-9jMzP7F4SDEaAnEyEALw_wcB&gclsrc=aw.ds&kw=&kwid=dsa-2473956379397&placement=&utm_campaign=CM2052283-search-google-nonbrand_162_-99_ES-National_e_all_acq_cpc_es-ES_DSA_Exact__dsa-2473956379397_739716807100_176004706265__m&utm_source=AdWords_NonBrand"
driver.get(url)
time.sleep(5)  # Espera a que cargue la página (ajusta según necesites)

# Estructura del JSON
datos = {
    "restaurante": {
        "nombre": "McDonald's Carabanchel",
        "plataforma": "Uber Eats",
        "direccion": "Carabanchel, Madrid",  # Ajusta si la página da la dirección exacta
        "productos": []
    }
}

# Busca los nombres y precios
try:
    # Encuentra todos los elementos con data-testid="rich-text" (nombres y precios)
    elementos = driver.find_elements(By.CSS_SELECTOR, "span[data-testid='rich-text']")

    # Variables temporales para emparejar nombres y precios
    nombre_actual = None

    for elemento in elementos:
        clases = elemento.get_attribute("class")
        
        # Si tiene las clases del nombre
        if "g1 fu g2 be dh bg di b1" in clases:
            nombre_actual = elemento.text.strip()
        
        # Si tiene las clases del precio y ya tenemos un nombre
        elif "g1 fu g2 be bf g4 di b1" in clases and nombre_actual:
            precio_texto = elemento.text.strip().replace("€", "").replace(",", ".").strip()
            try:
                precio = float(precio_texto)
                datos["restaurante"]["productos"].append({
                    "nombre": nombre_actual,
                    "precio": precio,
                    "fecha": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                nombre_actual = None  # Resetea para el próximo producto
            except ValueError:
                print(f"Error al convertir precio: {precio_texto}")

except Exception as e:
    print(f"Error en el scraping: {e}")

# Guarda en JSON
with open("scraped_data.json", "w", encoding="utf-8") as file:
    json.dump(datos, file, ensure_ascii=False, indent=4)

# Cierra el navegador
driver.quit()

print("Scraping completado. Datos guardados en scraped_data.json")