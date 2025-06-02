import React, { useState, useEffect } from 'react';
import axios from 'axios'; 
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'; 
import './App.css'; 

function App() {
  // ------------------- Estados principales -------------------
  const [productos, setProductos] = useState([]); // Lista de productos con sus precios actuales
  const [historial, setHistorial] = useState([]); // Historial de precios para un producto
  const [loading, setLoading] = useState(true); // Indicador de carga
  const [error, setError] = useState(null); // Manejo de errores
  const [searchTerm, setSearchTerm] = useState(''); // Término de búsqueda
  const [showModal, setShowModal] = useState(false); // Mostrar u ocultar el modal
  const [selectedProducto, setSelectedProducto] = useState(null); // Producto seleccionado para ver historial
  const [viewMode, setViewMode] = useState('tabla'); // Modo de visualización (tabla o gráfico)

  // ------------------- Filtros -------------------
  const [selectedRestaurants, setSelectedRestaurants] = useState([]); // Restaurantes seleccionados para el filtro
  const [selectedProducts, setSelectedProducts] = useState([]); // Productos seleccionados para el filtro

  // ------------------- Carga inicial de productos -------------------
  useEffect(() => {
    setLoading(true);
    axios.get('http://localhost:5000/api/productos') // Llama al backend para obtener productos
      .then(response => {
        // Asegura que los precios son números
        const datos = Array.isArray(response.data)
          ? response.data.map(p => ({
              ...p,
              precio_actual: parseFloat(p.precio_actual) || 0
            }))
          : [];
        setProductos(datos);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError('No se pudieron cargar los productos.');
        setLoading(false);
      });
  }, []);

  // ------------------- Inicializar filtros una vez cargados productos -------------------
  useEffect(() => {
    const restaurantes = [...new Set(productos.map(p => p.nombre_restaurante))];
    const productosUnicos = [...new Set(productos.map(p => p.nombre_producto))];

    if (!selectedRestaurants.length && restaurantes.length) {
      setSelectedRestaurants(restaurantes);
    }
    if (!selectedProducts.length && productosUnicos.length) {
      setSelectedProducts(productosUnicos);
    }
  }, [productos]);

  // ------------------- Ver historial de precios de un producto -------------------
  const verHistorial = (idProducto, nombreProducto, nombreRestaurante) => {
    setSelectedProducto({ idProducto, nombreProducto, nombreRestaurante });
    setLoading(true);
    axios.get(`http://localhost:5000/api/historico/${idProducto}`) // Llama al historial del producto
      .then(response => {
        const datos = Array.isArray(response.data)
          ? response.data.map(r => ({
              fecha: r.fecha_historico,
              precio: parseFloat(r.precio_historico) || 0
            }))
          : [];

        // Ordenar cronológicamente
        datos.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));

        setHistorial(datos);
        setViewMode('tabla');
        setShowModal(true);
        setLoading(false);
      });
  };

  // ------------------- Cerrar el modal -------------------
  const cerrarModal = () => {
    setShowModal(false);
    setHistorial([]);
    setSelectedProducto(null);
  };

  // ------------------- Datos únicos para desplegables de filtros -------------------
  const restaurantes = [...new Set(productos.map(p => p.nombre_restaurante))];
  const productosUnicos = [...new Set(productos.map(p => p.nombre_producto))];

  // ------------------- Aplicar filtros y búsqueda -------------------
  const restaurantesFiltrados = restaurantes.filter(r => selectedRestaurants.includes(r));
  const productosFiltrados = productosUnicos
    .filter(p => selectedProducts.includes(p))
    .filter(p => p.toLowerCase().includes(searchTerm.toLowerCase()));

  // ------------------- Determina si el precio actual es el más bajo -------------------
  const esPrecioMasBajo = (nombre, rest) => {
    const mismos = productos.filter(p => p.nombre_producto === nombre);
    const precios = mismos.map(p => p.precio_actual).filter(v => v > 0);
    if (!precios.length) return false;
    const min = Math.min(...precios);
    const prod = mismos.find(p => p.nombre_restaurante === rest);
    return prod && prod.precio_actual === min;
  };

  // ------------------- Renderizado condicional de estado -------------------
  if (loading) return <div>Cargando...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  // ------------------- Render principal -------------------
  return (
    <div className="App">
      <h1>Comparador de Precios - McDonald's Madrid</h1>

      {/* Modal para mostrar historial de precios */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Historial - {selectedProducto.nombreProducto} ({selectedProducto.nombreRestaurante})</h2>
            <div className="hist-controls">
              <button
                className={viewMode === 'tabla' ? 'active' : ''}
                onClick={() => setViewMode('tabla')}
              >Ver Tabla</button>
              <button
                className={viewMode === 'grafico' ? 'active' : ''}
                onClick={() => setViewMode('grafico')}
              >Ver Gráfico</button>
            </div>

            {/* Tabla o gráfico del historial */}
            {viewMode === 'tabla' ? (
              <table className="hist-table">
                <thead>
                  <tr><th>Fecha</th><th>Precio (€)</th></tr>
                </thead>
                <tbody>
                  {historial.map((h, i) => (
                    <tr key={i}>
                      <td>{new Date(h.fecha).toLocaleString()}</td>
                      <td>{h.precio.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={historial} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="fecha" tickFormatter={t => new Date(t).toLocaleDateString()} />
                    <YAxis />
                    <Tooltip labelFormatter={l => new Date(l).toLocaleString()} />
                    <Line type="monotone" dataKey="precio" stroke="#C8102E" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            <button className="close-button" onClick={cerrarModal}>Cerrar</button>
          </div>
        </div>
      )}

      {/* Filtros para restaurantes y productos */}
      <div className="filters">
        <details className="filter-group">
          <summary>Filtrar Restaurantes</summary>
          {/* Opción para seleccionar todos */}
          <label className="dropdown-item" style={{ fontWeight: 'bold' }}>
            <input
              type="checkbox"
              checked={selectedRestaurants.length === restaurantes.length && restaurantes.length > 0}
              onChange={e => {
                setSelectedRestaurants(e.target.checked ? restaurantes : []);
              }}
            /> Seleccionar todo
          </label>
          {/* Lista de restaurantes */}
          {restaurantes.map((rest, i) => (
            <label key={i} className="dropdown-item">
              <input
                type="checkbox"
                value={rest}
                checked={selectedRestaurants.includes(rest)}
                onChange={e => {
                  const { checked, value } = e.target;
                  setSelectedRestaurants(prev =>
                    checked ? [...prev, value] : prev.filter(r => r !== value)
                  );
                }}
              /> {rest}
            </label>
          ))}
        </details>

        <details className="filter-group">
          <summary>Filtrar Productos</summary>
          {/* Opción para seleccionar todos */}
          <label className="dropdown-item" style={{ fontWeight: 'bold' }}>
            <input
              type="checkbox"
              checked={selectedProducts.length === productosUnicos.length && productosUnicos.length > 0}
              onChange={e => {
                setSelectedProducts(e.target.checked ? productosUnicos : []);
              }}
            /> Seleccionar todo
          </label>
          {/* Lista de productos */}
          {productosUnicos.map((prod, i) => (
            <label key={i} className="dropdown-item">
              <input
                type="checkbox"
                value={prod}
                checked={selectedProducts.includes(prod)}
                onChange={e => {
                  const { checked, value } = e.target;
                  setSelectedProducts(prev =>
                    checked ? [...prev, value] : prev.filter(p => p !== value)
                  );
                }}
              /> {prod}
            </label>
          ))}
        </details>
      </div>

      {/* Campo de búsqueda de productos */}
      <div className="search-container">
        <input
          type="text"
          placeholder="Buscar producto..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Tabla comparativa de precios */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Producto</th>
              {restaurantesFiltrados.map((rest, idx) => <th key={idx}>{rest}</th>)}
            </tr>
          </thead>
          <tbody>
            {productosFiltrados.map((prod, idx) => (
              <tr key={idx}>
                <td>{prod}</td>
                {restaurantesFiltrados.map((rest, j) => {
                  const item = productos.find(
                    p => p.nombre_restaurante === rest && p.nombre_producto === prod
                  );
                  return (
                    <td key={j}>
                      {item ? (
                        <button
                          className={`price-button ${esPrecioMasBajo(prod, rest) ? 'precio-mas-bajo' : ''}`}
                          onClick={() => verHistorial(item.id_producto, item.nombre_producto, item.nombre_restaurante)}
                        >
                          {item.precio_actual.toFixed(2)} €
                        </button>
                      ) : ('-')}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
