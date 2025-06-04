#  ComparadorDePrecios

##  Despliegue de la Aplicación

Sigue estos pasos para desplegar correctamente la aplicación en local:

1. **Cargar los datos en tu base de datos local**  
   - Ve a la carpeta `dump` y carga los datos en tu BBDD local.

2. **Iniciar el servidor backend**  
   - Abre una terminal en la carpeta `backend`  
   - Ejecuta el siguiente comando:
     ```bash
     node server.js
     ```

3. **Iniciar el frontend**  
   - Abre otra terminal en la carpeta `frontend`  
   - Ejecuta el siguiente comando:
     ```bash
     npm run dev
     ```

---

## Ejecutar el scrappeo y carga de datos a la BBDD

- Abre una terminal en la raiz del proyecto
- Ejecuta el siguiente comando
    ```bash
     .\run_scraper.bat
    ```
- Este comando ejecuta el script por lotes de Windos que ejecuta de forma secuencial 'scraper.py' y 'db_loader.py' 


