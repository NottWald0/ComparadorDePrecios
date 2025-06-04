const express = require('express');  
const mysql = require('mysql2');     
const cors = require('cors');        


//Con esto manejo las rutas y peticiones
const app = express();
app.use(cors());
app.use(express.json()); 


//Me conecto a la BBBDD
const connection = mysql.createConnection({
    host: 'localhost', 
    user: 'root',      
    password: 'root', 
    database: 'comparador_de_precios' 
});

// Intento conectarme a la base de datos y compruebo si hay errores
connection.connect((err) => {
    if (err) {
        console.error('Error al conectar a MySQL:', err); 
        return;
    }
    console.log('Conectado a la base de datos MySQL'); 
});

// Creo un ENDPOINT para obtener todos los productos con sus precios y el restaurante
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
    
    connection.query(query, (err, results) => {
        if (err) {
            console.error('Error al consultar los productos:', err); 
            res.status(500).json({ error: 'Error al obtener los datos' }); 
            return;
        }
        res.json(results); // Envio los datos  en formato JSON
    });
});

// Creo un ENDPOINT para obtener el historial de precios de un producto 
app.get('/api/historico/:id_producto', (req, res) => {
    const id_producto = req.params.id_producto; 
    // Con esta consulta obtengo el historial de un producto
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
    // Ejecuto la consulta
    connection.query(query, [id_producto], (err, results) => {
        if (err) {
            console.error('Error al consultar el historial:', err); 
            res.status(500).json({ error: 'Error al obtener el historial' }); 
            return;
        }
        res.json(results); 
    });
});

// Inicio el servidor en el puerto 5000
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`); 
});