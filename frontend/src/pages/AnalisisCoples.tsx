// src/pages/AnalisisCoples.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Settings,
  Assessment,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { analisisAPI } from '../api/analisis';
import type { AnalisisCopleList, EstadoSistema } from '../api/analisis';
import AnalisisCard from '../components/AnalisisCard';
import EstadisticasCard from '../components/EstadisticasCard';
import TestColorComponent from '../components/TestColorComponent';
import { useAuth } from '../context/AuthContext';
import Swal from 'sweetalert2';

const AnalisisCoples: React.FC = () => {
  const navigate = useNavigate();
  const { } = useAuth();
  const [estadoSistema, setEstadoSistema] = useState<EstadoSistema | null>(null);
  const [analisisRecientes, setAnalisisRecientes] = useState<AnalisisCopleList[]>([]);
  const [estadisticas, setEstadisticas] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [tipoAnalisis, setTipoAnalisis] = useState<'completo' | 'clasificacion'>('completo');

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [estado, recientes, stats] = await Promise.all([
        analisisAPI.getEstadoSistema(),
        analisisAPI.getAnalisisRecientes(6),
        analisisAPI.getEstadisticas(),
      ]);
      
      setEstadoSistema(estado);
      setAnalisisRecientes(recientes);
      setEstadisticas(stats);
    } catch (error) {
      console.error('Error cargando datos:', error);
      Swal.fire('Error', 'Error al cargar los datos del sistema', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRealizarAnalisis = async () => {
    try {
      setProcesando(true);
      
      const resultado = await analisisAPI.realizarAnalisis({
        tipo_analisis: tipoAnalisis,
      });

      console.log('🔍 Respuesta del análisis:', resultado);

      if (resultado.analisis) {
        console.log('✅ Análisis encontrado en respuesta:', resultado.analisis.id_analisis);
        Swal.fire({
          title: 'Análisis Completado',
          text: `Análisis ${resultado.analisis.id_analisis} completado exitosamente`,
          icon: 'success',
          timer: 3000,
        });
        
        // Recargar datos
        console.log('🔄 Recargando datos...');
        await cargarDatos();
        console.log('✅ Datos recargados');
      } else {
        console.log('❌ No se encontró análisis en la respuesta:', resultado);
      }
    } catch (error) {
      console.error('Error realizando análisis:', error);
      Swal.fire('Error', 'Error al realizar el análisis', 'error');
    } finally {
      setProcesando(false);
    }
  };

  const handleInicializarSistema = async () => {
    try {
      if (!estadoSistema?.configuracion_activa) {
        Swal.fire('Error', 'No hay configuración activa disponible', 'error');
        return;
      }

      await analisisAPI.inicializarSistema({
        configuracion_id: estadoSistema.configuracion_activa.id,
      });

      Swal.fire('Éxito', 'Sistema inicializado correctamente', 'success');
      await cargarDatos();
    } catch (error) {
      console.error('Error inicializando sistema:', error);
      Swal.fire('Error', 'Error al inicializar el sistema', 'error');
    }
  };

  const handleLiberarSistema = async () => {
    try {
      await analisisAPI.liberarSistema();
      Swal.fire('Éxito', 'Sistema liberado correctamente', 'success');
      await cargarDatos();
    } catch (error) {
      console.error('Error liberando sistema:', error);
      Swal.fire('Error', 'Error al liberar el sistema', 'error');
    }
  };

  const handleVerAnalisis = (id: number) => {
    navigate(`/analisis/${id}`);
  };

  const handleDescargarAnalisis = (id: number) => {
    // Implementar descarga de resultados
    console.log('Descargar análisis:', id);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Sistema de Análisis de Coples
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<Settings />}
            onClick={() => navigate('/analisis/configuraciones')}
          >
            Configuraciones
          </Button>
          <Button
            variant="outlined"
            startIcon={<Assessment />}
            onClick={() => navigate('/analisis/estadisticas')}
          >
            Estadísticas
          </Button>
        </Box>
      </Box>

      {/* Estado del Sistema */}
      <Card sx={{ 
        mb: 3, 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
      }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
              Estado del Sistema
            </Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<Refresh />}
                onClick={cargarDatos}
                sx={{ 
                  color: 'white', 
                  borderColor: 'white',
                  '&:hover': { 
                    borderColor: 'white', 
                    backgroundColor: 'rgba(255,255,255,0.1)' 
                  }
                }}
              >
                Actualizar
              </Button>
              {estadoSistema?.inicializado ? (
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  startIcon={<Stop />}
                  onClick={handleLiberarSistema}
                  sx={{ 
                    color: 'white', 
                    borderColor: 'white',
                    '&:hover': { 
                      borderColor: 'white', 
                      backgroundColor: 'rgba(255,255,255,0.1)' 
                    }
                  }}
                >
                  Liberar
                </Button>
              ) : (
                <Button
                  variant="outlined"
                  color="success"
                  size="small"
                  startIcon={<PlayArrow />}
                  onClick={handleInicializarSistema}
                  sx={{ 
                    color: 'white', 
                    borderColor: 'white',
                    '&:hover': { 
                      borderColor: 'white', 
                      backgroundColor: 'rgba(255,255,255,0.1)' 
                    }
                  }}
                >
                  Inicializar
                </Button>
              )}
            </Box>
          </Box>

          <Box display="flex" flexWrap="wrap" gap={3} justifyContent="space-around">
            <Box textAlign="center" minWidth="200px">
              <Chip
                label={estadoSistema?.inicializado ? 'Inicializado' : 'No Inicializado'}
                color={estadoSistema?.inicializado ? 'success' : 'error'}
                variant="filled"
                sx={{ 
                  backgroundColor: estadoSistema?.inicializado ? 'rgba(76, 175, 80, 0.9)' : 'rgba(244, 67, 54, 0.9)',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '0.9rem'
                }}
              />
              <Typography variant="body2" sx={{ mt: 1, color: 'rgba(255,255,255,0.8)' }}>
                Estado del Sistema
              </Typography>
            </Box>
            <Box textAlign="center" minWidth="200px">
              <Typography variant="body1" fontWeight="bold" sx={{ color: 'white' }}>
                {estadoSistema?.configuracion_activa?.nombre || 'Sin configuración'}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                Configuración Activa
              </Typography>
            </Box>
            <Box textAlign="center" minWidth="200px">
              <Typography variant="body1" fontWeight="bold" sx={{ color: 'white' }}>
                {estadoSistema?.configuracion_activa?.umbral_confianza || 'N/A'}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                Umbral de Confianza
              </Typography>
            </Box>
            <Box textAlign="center" minWidth="200px">
              <Typography variant="body1" fontWeight="bold" sx={{ color: 'white' }}>
                {estadoSistema?.configuracion_activa?.configuracion_robustez || 'N/A'}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                Robustez
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Estadísticas */}
      {estadisticas && (
        <Box mb={3}>
          <EstadisticasCard estadisticas={estadisticas.base_datos} />
        </Box>
      )}

      {/* Componente de Prueba de Colores */}
      <TestColorComponent />

      {/* Control de Análisis */}
      <Card sx={{ 
        mb: 3, 
        background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        color: 'white',
        boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
      }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
            Realizar Análisis
          </Typography>
          <Box display="flex" gap={2} alignItems="center">
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel sx={{ color: 'white' }}>Tipo de Análisis</InputLabel>
              <Select
                value={tipoAnalisis}
                onChange={(e) => setTipoAnalisis(e.target.value as any)}
                label="Tipo de Análisis"
                sx={{ 
                  color: 'white',
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'white',
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'white',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'white',
                  },
                  '& .MuiSvgIcon-root': {
                    color: 'white',
                  },
                }}
              >
                <MenuItem value="completo">Análisis Completo</MenuItem>
                <MenuItem value="clasificacion">Solo Clasificación</MenuItem>
              </Select>
            </FormControl>
            <Button
              variant="contained"
              startIcon={<PlayArrow />}
              onClick={handleRealizarAnalisis}
              disabled={procesando || !estadoSistema?.inicializado}
              sx={{
                backgroundColor: 'rgba(255,255,255,0.2)',
                color: 'white',
                border: '1px solid white',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.3)',
                },
                '&:disabled': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  color: 'rgba(255,255,255,0.5)',
                }
              }}
            >
              {procesando ? 'Procesando...' : 'Iniciar Análisis'}
            </Button>
          </Box>
          {!estadoSistema?.inicializado && (
            <Alert severity="warning" sx={{ mt: 2, backgroundColor: 'rgba(255,255,255,0.1)' }}>
              El sistema debe estar inicializado para realizar análisis
            </Alert>
          )}
        </CardContent>
      </Card>


      {/* Análisis Recientes */}
      <Card sx={{ 
        background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        color: 'white',
        boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
      }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
            Análisis Recientes
          </Typography>
          {analisisRecientes.length === 0 ? (
            <Typography sx={{ color: 'rgba(255,255,255,0.8)', textAlign: 'center', py: 4 }}>
              No hay análisis recientes
            </Typography>
          ) : (
            <Box display="flex" flexWrap="wrap" gap={2}>
              {analisisRecientes.map((analisis) => (
                <Box key={analisis.id} minWidth="300px" flex="1 1 300px">
                  <AnalisisCard
                    analisis={analisis}
                    onView={handleVerAnalisis}
                    onDownload={handleDescargarAnalisis}
                  />
                </Box>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default AnalisisCoples;
