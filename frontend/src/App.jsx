import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import './App.css';

function App() {
  // Estados para datos y UI
  const [productos, setProductos] = useState([]);
  const [historial, setHistorial] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedProducto, setSelectedProducto] = useState(null);
  const [viewMode, setViewMode] = useState('tabla'); // 'tabla' o 'grafico'

  // Estados para filtros
  const [selectedRestaurants, setSelectedRestaurants] = useState([]);
  const [selectedProducts, setSelectedProducts] = useState([]);

  // Carga inicial de productos
  useEffect(() => {
    setLoading(true);
    axios.get('http://localhost:5000/api/productos')
      .then(response => {
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

  // Inicializar filtros tras cargar productos
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

  // Función para obtener historial y abrir modal
  const verHistorial = (idProducto, nombreProducto, nombreRestaurante) => {
    setSelectedProducto({ idProducto, nombreProducto, nombreRestaurante });
    setLoading(true);
    axios.get(`http://localhost:5000/api/historico/${idProducto}`)
  .then(response => {
    const datos = Array.isArray(response.data)
      ? response.data.map(r => ({
          fecha: r.fecha_historico,
          precio: parseFloat(r.precio_historico) || 0
        }))
      : [];

    // Ordena de más antiguo a más reciente:
    datos.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));

    setHistorial(datos);
    setViewMode('tabla');
    setShowModal(true);
    setLoading(false);
  })
  };

  // Cerrar modal
  const cerrarModal = () => {
    setShowModal(false);
    setHistorial([]);
    setSelectedProducto(null);
  };

  // Datos únicos para filtros
  const restaurantes = [...new Set(productos.map(p => p.nombre_restaurante))];
  const productosUnicos = [...new Set(productos.map(p => p.nombre_producto))];

  // Aplicar filtros y búsqueda
  const restaurantesFiltrados = restaurantes.filter(r => selectedRestaurants.includes(r));
  const productosFiltrados = productosUnicos
    .filter(p => selectedProducts.includes(p))
    .filter(p => p.toLowerCase().includes(searchTerm.toLowerCase()));

  // Determinar precio más bajo
  const esPrecioMasBajo = (nombre, rest) => {
    const mismos = productos.filter(p => p.nombre_producto === nombre);
    const precios = mismos.map(p => p.precio_actual).filter(v => v > 0);
    if (!precios.length) return false;
    const min = Math.min(...precios);
    const prod = mismos.find(p => p.nombre_restaurante === rest);
    return prod && prod.precio_actual === min;
  };

  if (loading) return <div>Cargando...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div className="App">
      <h1>Comparador de Precios - McDonald's Madrid</h1>

      {/* Modal emergente de Historial */}
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

       {/* Filtros en desplegable */}
<div className="filters">
  <details className="filter-group">
    <summary>Filtrar Restaurantes</summary>
    <label className="dropdown-item" style={{ fontWeight: 'bold' }}>
      <input
        type="checkbox"
        checked={selectedRestaurants.length === restaurantes.length && restaurantes.length > 0}
        onChange={e => {
          if (e.target.checked) {
            setSelectedRestaurants(restaurantes);
          } else {
            setSelectedRestaurants([]);
          }
        }}
      /> Seleccionar todo
    </label>
    {restaurantes.map((rest, i) => (
      <label key={i} className="dropdown-item">
        <input
          type="checkbox"
          value={rest}
          checked={selectedRestaurants.includes(rest)}
          onChange={e => {
            const { checked, value } = e.target;
            setSelectedRestaurants(prev => {
              if (checked) {
                const nuevo = [...prev, value];
                return nuevo;
              } else {
                return prev.filter(r => r !== value);
              }
            });
          }}
        /> {rest}
      </label>
    ))}
  </details>
  <details className="filter-group">
    <summary>Filtrar Productos</summary>
    <label className="dropdown-item" style={{ fontWeight: 'bold' }}>
      <input
        type="checkbox"
        checked={selectedProducts.length === productosUnicos.length && productosUnicos.length > 0}
        onChange={e => {
          if (e.target.checked) {
            setSelectedProducts(productosUnicos);
          } else {
            setSelectedProducts([]);
          }
        }}
      /> Seleccionar todo
    </label>
    {productosUnicos.map((prod, i) => (
      <label key={i} className="dropdown-item">
        <input
          type="checkbox"
          value={prod}
          checked={selectedProducts.includes(prod)}
          onChange={e => {
            const { checked, value } = e.target;
            setSelectedProducts(prev => {
              if (checked) {
                return [...prev, value];
              } else {
                return prev.filter(p => p !== value);
              }
            });
          }}
        /> {prod}
      </label>
    ))}
  </details>
</div>

      {/* Buscador */}
      <div className="search-container">
        <input
          type="text"
          placeholder="Buscar producto..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Tabla de precios */}
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
