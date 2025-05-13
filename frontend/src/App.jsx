import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Componente principal de la aplicación
function App() {
    // Estados para manejar los datos y la interfaz
    const [productos, setProductos] = useState([]); // Lista de productos y precios actuales
    const [historial, setHistorial] = useState([]); // Historial de precios de un producto seleccionado
    const [loading, setLoading] = useState(true); // Indicador de carga mientras se obtienen datos
    const [error, setError] = useState(null); // Mensaje de error si falla una solicitud
    const [searchTerm, setSearchTerm] = useState(''); // Término de búsqueda para filtrar productos
    const [showModal, setShowModal] = useState(false); // Controla si el modal está visible o no
    const [selectedProducto, setSelectedProducto] = useState(null); // Producto seleccionado para ver su historial

    // Efecto para cargar los productos al montar el componente
    useEffect(() => {
        setLoading(true); // Activa el estado de carga
        // Realiza una petición GET al backend para obtener la lista de productos
        axios.get('http://localhost:5000/api/productos')
            .then(response => {
                // Verifica si la respuesta es valida
                if (Array.isArray(response.data)) {
                    // Parseo los precios  para evitar problemas de formato
                    const productosConPreciosNumericos = response.data.map(producto => ({
                        ...producto,
                        precio_actual: parseFloat(producto.precio_actual) || 0
                    }));
                    setProductos(productosConPreciosNumericos); // Actualiza el estado con los productos procesados
                } else {
                    setProductos([]); // Si no es un arreglo, establece una lista vacía
                }
                setLoading(false); // Desactiva el estado de carga
            })
            .catch(error => {
                // Maneja errores en la petición y muestra un mensaje al usuario
                console.error('Error al obtener los productos:', error);
                setError('No se pudieron cargar los productos. Asegúrate de que el backend esté corriendo.');
                setLoading(false); // Desactiva el estado de carga incluso si hay error
            });
    }, []); // El arreglo vacío asegura que esto solo se ejecute al montar el componente

    //--------------------------------------------------------------------------------------------------------------------------------------------
    // Función para obtener y mostrar el historial de precios de un producto
    const verHistorial = (idProducto, nombreProducto, nombreRestaurante) => {
        setSelectedProducto({ idProducto, nombreProducto, nombreRestaurante }); // Almacena el producto seleccionado
        setLoading(true); // Activa el estado de carga
        // Petición GET al backend para obtener el historial del producto
        axios.get(`http://localhost:5000/api/historico/${idProducto}`)
            .then(response => {
                if (Array.isArray(response.data)) {
                    // Convierte los precios históricos a números flotantes
                    const historialConPreciosNumericos = response.data.map(registro => ({
                        ...registro,
                        precio_historico: parseFloat(registro.precio_historico) || 0
                    }));
                    setHistorial(historialConPreciosNumericos); // Actualiza el estado con el historial
                } else {
                    setHistorial([]); // Si no es un arreglo, establece una lista vacía
                }
                setShowModal(true); // Muestra el modal con el historial
                setLoading(false); // Desactiva el estado de carga
            })
            .catch(error => {
                // Maneja errores y muestra un mensaje al usuario
                console.error('Error al obtener el historial:', error);
                setError('No se pudo cargar el historial.');
                setLoading(false); // Desactiva el estado de carga
            });
    };

    //--------------------------------------------------------------------------------------------------------------------------------------------
    // Función para cerrar el modal y limpiar datos relacionados
    const cerrarModal = () => {
        setShowModal(false); // Oculta el modal
        setHistorial([]); // Limpia el historial del estado
        setSelectedProducto(null); // Elimina el producto seleccionado
    };

    // Crea una lista única de restaurantes a partir de los productos
    const restaurantes = [...new Set(productos.map(p => p.nombre_restaurante))];

    // Filtra los nombres de productos únicos según el término de búsqueda
    const productosUnicos = [...new Set(productos.map(p => p.nombre_producto))].filter(nombre =>
        nombre.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Determina si un precio es el más bajo para un producto entre todos los restaurantes
    const esPrecioMasBajo = (productoNombre, restaurante) => {
        // Filtra los productos con el mismo nombre
        const productosDeEsteTipo = productos.filter(
            p => p.nombre_producto === productoNombre
        );
        // Extrae los precios válidos 
        const precios = productosDeEsteTipo
            .map(p => p.precio_actual)
            .filter(precio => typeof precio === 'number' && precio > 0);
        if (precios.length === 0) return false; // No hay precios válidos para comparar
        const precioMinimo = Math.min(...precios); // Encuentra el precio más bajo
        // Busca el precio del producto en el restaurante especificado
        const producto = productos.find(
            p => p.nombre_restaurante === restaurante && p.nombre_producto === productoNombre
        );
        const precioActual = producto ? producto.precio_actual : null;
        return precioActual === precioMinimo; // Devuelve true si es el precio más bajo
    };

    // Renderizado condicional mientras se cargan los datos
    if (loading) {
        return <div>Cargando...</div>; // Muestra un mensaje de carga
    }

    // Renderizado condicional si hay un error
    if (error) {
        return <div style={{ color: 'red' }}>{error}</div>; // Muestra el error en rojo
    }

    // Renderizado principal de la interfaz
    return (
        <div className="App">
            <h1>Comparador de Precios - McDonald's Madrid</h1>

            {/* Campo de búsqueda para filtrar productos */}
            <div className="search-container">
                <input
                    type="text"
                    placeholder="Buscar producto..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)} // Actualiza el término de búsqueda al escribir
                />
            </div>

            <div className="main-container">
                {/* Tabla de precios con restaurantes como columnas y productos como filas */}
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Producto</th> {/* Columna para los nombres de productos */}
                                {restaurantes.map((restaurante, index) => (
                                    <th key={index}>{restaurante}</th> // Columnas con nombres de restaurantes
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {productosUnicos.map((productoNombre, index) => (
                                <tr key={index}>
                                    <td>{productoNombre}</td> {/* Nombre del producto en la fila */}
                                    {restaurantes.map((restaurante, idx) => {
                                        // Busca el producto en el restaurante actual
                                        const producto = productos.find(
                                            p => p.nombre_restaurante === restaurante && p.nombre_producto === productoNombre
                                        );
                                        return (
                                            <td key={idx}>
                                                {producto ? (
                                                    // Botón con el precio, resaltado si es el más bajo
                                                    <button
                                                        className={`price-button ${
                                                            esPrecioMasBajo(productoNombre, restaurante)
                                                                ? 'precio-mas-bajo'
                                                                : ''
                                                        }`}
                                                        onClick={() =>
                                                            verHistorial(
                                                                producto.id_producto,
                                                                producto.nombre_producto,
                                                                producto.nombre_restaurante
                                                            )
                                                        } // Muestra el historial al hacer clic
                                                    >
                                                        {producto.precio_actual.toFixed(2)} € {/* Precio formateado */}
                                                    </button>
                                                ) : (
                                                    '-' // Muestra "-" si no hay precio disponible
                                                )}
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal para mostrar el historial de precios */}
            {showModal && (
                <div className="modal-overlay">
                    <div className="modal">
                        <h2>
                            Historial de Precios - {selectedProducto?.nombre_producto} ({selectedProducto?.nombre_restaurante})
                        </h2> {/* Título con el nombre del producto y restaurante */}
                        {historial.length === 0 ? (
                            <p>No hay datos históricos disponibles.</p> // Mensaje si no hay historial
                        ) : (
                            <table>
                                <thead>
                                    <tr>
                                        <th>Precio (€)</th>
                                        <th>Fecha</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {historial.map((registro, index) => (
                                        <tr key={index}>
                                            <td>{registro.precio_historico.toFixed(2)}</td> {/* Precio histórico formateado */}
                                            <td>{new Date(registro.fecha_historico).toLocaleString()}</td> {/* Fecha formateada */}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                        <button className="close-button" onClick={cerrarModal}>
                            Cerrar
                        </button> {/* Botón para cerrar el modal */}
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;