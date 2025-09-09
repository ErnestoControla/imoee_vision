import { Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Layout from './components/Layout';
import NotFound from './pages/NotFound';
import HomePage from './pages/HomePage';
import Usuarios from './pages/Usuarios';
import Roles from './pages/Roles';              // ← Importa tu página de Roles
import AdminRoute from './components/AdminRoute';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/login" element={<LoginPage />} />

      {/* Rutas que necesitan sesión */}
      <Route element={<PrivateRoute />}>
        {/* Dentro del guard, aplicamos el Layout */}
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/usuarios" element={<Usuarios />} />
          <Route
            path="/roles"
            element={
              <AdminRoute>
                <Roles />
              </AdminRoute>
            }
          />
          {/* Aquí más rutas internas protegidas */}
        </Route>
      </Route>

      {/* Cualquier otra */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
