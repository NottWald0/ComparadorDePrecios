// Importo las librerías necesarias para el servidor
const express = require('express');  // Express: para crear el servidor y manejar rutas
const mysql = require('mysql2');     // mysql2: para conectarse a la base de datos MySQL
const cors = require('cors');        // cors: para permitir que el frontend haga peticiones desde otro puerto


// Creo una aplicación de Express para manejar las rutas y peticiones
const app = express();
app.use(cors()); // Habilito CORS para que el frontend pueda hacer peticiones desde otro puerto 
app.use(express.json()); // Para parsear JSON en las peticiones que reciba el servidor


// Configuro la conexión a mi base de datos MySQL
const connection = mysql.createConnection({
    host: 'localhost', 
    user: 'root',      
    password: 'root', 
    database: 'comparador_de_precios' 
});

// Intento conectarme a la base de datos y compruebo si hay errores
connection.connect((err) => {
    if (err) {
        console.error('Error al conectar a MySQL:', err); // Muestro el error si falla la conexión
        return;
    }
    console.log('Conectado a la base de datos MySQL'); 
});

// Creo una ruta para obtener todos los productos con sus precios y el restaurante
app.get('/api/productos', (req, res) => {
   
    // Esta consulta me permite obtener el nombre del producto, el nombre del restaurante, el precio actual y la fecha
    const query = `
        SELECT 
            p.id_producto,
            p.nombre AS nombre_producto,
            r.nombre AS nombre_restaurante,
            pr.precio AS precio_actual,
            pr.fecha AS fecha_actual
        FROM Productos p
        JOIN Restaurante r ON p.id_restaurante = r.id_restaurante
        JOIN Precio pr ON p.id_producto = pr.id_producto
        ORDER BY p.nombre, r.nombre
    `;
    // Ejecuto la consulta en la base de datos
    connection.query(query, (err, results) => {
        if (err) {
            console.error('Error al consultar los productos:', err); // Muestro el error si la consulta falla
            res.status(500).json({ error: 'Error al obtener los datos' }); // Envío un error al cliente
            return;
        }
        res.json(results); // Envio los datos al cliente en formato JSON
    });
});

// Creo una ruta para obtener el historial de precios de un producto específico
app.get('/api/historico/:id_producto', (req, res) => {
    const id_producto = req.params.id_producto; 
    // Con esta consulta obtengo el historial de un producto, uniendo las tablas Historico, Productos y Restaurante
    const query = `
        SELECT 
            h.precio AS precio_historico,
            h.fecha AS fecha_historico,
            p.nombre AS nombre_producto,
            r.nombre AS nombre_restaurante
        FROM Historico h
        JOIN Productos p ON h.id_producto = p.id_producto
        JOIN Restaurante r ON p.id_restaurante = r.id_restaurante
        WHERE h.id_producto = ?
        ORDER BY h.fecha DESC
    `;
    // Ejecuto la consulta, pasando el id_producto como parámetro 
    connection.query(query, [id_producto], (err, results) => {
        if (err) {
            console.error('Error al consultar el historial:', err); // Muestro el error si la consulta falla
            res.status(500).json({ error: 'Error al obtener el historial' }); // Envío un error al cliente
            return;
        }
        res.json(results); // Envío el historial al cliente en formato JSON
    });
});

// Inicio el servidor en el puerto 5000
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`); // Confirmo que el servidor está funcionando
});