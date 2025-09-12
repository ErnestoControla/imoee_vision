import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Button,
  Chip,
  Grid,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import {
  ArrowBack,
  Download,
  Image
} from '@mui/icons-material';
import dayjs from 'dayjs';
import ImagenProcesada from '../components/ImagenProcesada';
import API from '../api/axios';

interface AnalisisCople {
  id: number;
  estado: string;
  tipo_analisis: string;
  timestamp_captura: string;
  timestamp_procesamiento: string;
  usuario_nombre: string;
  configuracion_nombre: string;
  resolucion_ancho: number;
  resolucion_alto: number;
  resolucion_canales: number;
  tiempo_total_ms: number;
  mensaje_error?: string;
  resultado_clasificacion?: {
    clase_predicha: string;
    confianza: number;
    tiempo_inferencia_ms: number;
  };
  detecciones_defectos?: Array<{
    clase: string;
    confianza: number;
    centroide: { x: number; y: number };
    area: number;
  }>;
  detecciones_piezas?: Array<{
    clase: string;
    confianza: number;
    centroide: { x: number; y: number };
    area: number;
  }>;
  metadatos_json?: {
    tiempos?: {
      captura_ms?: number;
      segmentacion_defectos_ms?: number;
      segmentacion_piezas_ms?: number;
      clasificacion_ms?: number;
      deteccion_defectos_ms?: number;
      deteccion_piezas_ms?: number;
      total_ms?: number;
    };
    resultados?: {
      defectos_segmentadas?: Array<{
        id?: number;
        clase: string;
        confianza: number;
        centroide: { x: number; y: number };
        area_mascara: number;
        area_bbox?: number;
        bbox?: { x1: number; y1: number; x2: number; y2: number };
      }>;
      piezas_segmentadas?: Array<{
        id?: number;
        clase: string;
        confianza: number;
        centroide: { x: number; y: number };
        area_mascara: number;
        area_bbox?: number;
        bbox?: { x1: number; y1: number; x2: number; y2: number };
      }>;
      clasificacion?: {
        clase_predicha: string;
        confianza: number;
      };
    };
    modelo?: {
      nombre: string;
    };
  };
}

const DetalleAnalisis: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [analisis, setAnalisis] = useState<AnalisisCople | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalisis = async () => {
      try {
        const response = await API.get(`/analisis/resultados/${id}/`);
        setAnalisis(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchAnalisis();
    }
  }, [id]);

  const formatTiempo = (ms: number): string => {
    if (ms === 0 || isNaN(ms)) return '0ms';
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const getEstadoColor = (estado: string): string => {
    switch (estado) {
      case 'completado': return 'success';
      case 'procesando': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getTipoAnalisisLabel = (tipo: string): string => {
    switch (tipo) {
      case 'clasificacion': return 'Clasificación';
      case 'deteccion_defectos': return 'Detección de Defectos';
      case 'deteccion_piezas': return 'Detección de Piezas';
      case 'segmentacion_defectos': return 'Segmentación de Defectos';
      case 'segmentacion_piezas': return 'Segmentación de Piezas';
      default: return tipo;
    }
  };

  const handleDescargar = () => {
    // TODO: Implementar descarga
    console.log('Descargar análisis:', analisis?.id);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !analisis) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          {error || 'No se pudo cargar el análisis'}
        </Alert>
        <Button
          variant="outlined"
          startIcon={<ArrowBack />}
          onClick={() => navigate('/analisis')}
          sx={{ mt: 2 }}
        >
          Volver
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBack />}
          onClick={() => navigate('/analisis')}
        >
          Volver
        </Button>
        <Typography variant="h4" component="h1">
          Detalle del Análisis
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Imagen Procesada - Fila Superior */}
        <Grid size={{ xs: 12 }}>
          {analisis.estado === 'completado' && (
            <Card sx={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
            }}>
              <CardHeader
                title="Imagen Procesada"
                avatar={<Image sx={{ color: 'white' }} />}
                action={
                  <Button
                    startIcon={<Download />}
                    variant="contained"
                    color="primary"
                    onClick={handleDescargar}
                    sx={{ 
                      backgroundColor: 'rgba(255,255,255,0.2)',
                      '&:hover': {
                        backgroundColor: 'rgba(255,255,255,0.3)',
                      }
                    }}
                  >
                    DESCARGAR
                  </Button>
                }
                sx={{ color: 'white' }}
              />
              <CardContent sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center',
                minHeight: '400px',
                p: 1
              }}>
                <Box sx={{ 
                  maxWidth: '100%', 
                  maxHeight: '100%',
                  '& img': {
                    maxWidth: '100%',
                    maxHeight: '100%',
                    objectFit: 'contain'
                  }
                }}>
                  <ImagenProcesada 
                    analisisId={analisis.id} 
                    showThumbnail={false}
                    width={600}
                    height={600}
                  />
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Información - Fila Inferior */}
        <Grid size={{ xs: 12 }}>
          <Grid container spacing={3}>
            {/* Columna Izquierda - Información General */}
            <Grid size={{ xs: 12, md: 4 }}>
              <Card sx={{ mb: 2 }}>
                <CardHeader
                  title="Información General"
                  subheader={
                    <Box display="flex" gap={1} alignItems="center" flexWrap="wrap">
                      <Chip
                        label={analisis.estado}
                        color={getEstadoColor(analisis.estado) as any}
                        size="small"
                      />
                      <Chip
                        label={getTipoAnalisisLabel(analisis.tipo_analisis)}
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  }
                />
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid size={12}>
                      <Typography variant="body2" color="text.secondary">
                        Fecha de Captura:
                      </Typography>
                      <Typography variant="body1">
                        {dayjs(analisis.timestamp_captura).format('DD/MM/YYYY HH:mm:ss')}
                      </Typography>
                    </Grid>
                    <Grid size={12}>
                      <Typography variant="body2" color="text.secondary">
                        Fecha de Procesamiento:
                      </Typography>
                      <Typography variant="body1">
                        {dayjs(analisis.timestamp_procesamiento).format('DD/MM/YYYY HH:mm:ss')}
                      </Typography>
                    </Grid>
                    <Grid size={12}>
                      <Typography variant="body2" color="text.secondary">
                        Usuario:
                      </Typography>
                      <Typography variant="body1">
                        {analisis.usuario_nombre}
                      </Typography>
                    </Grid>
                    <Grid size={12}>
                      <Typography variant="body2" color="text.secondary">
                        Configuración:
                      </Typography>
                      <Typography variant="body1">
                        {analisis.configuracion_nombre}
                      </Typography>
                    </Grid>
                    <Grid size={12}>
                      <Typography variant="body2" color="text.secondary">
                        Resolución:
                      </Typography>
                      <Typography variant="body1">
                        {analisis.resolucion_ancho} x {analisis.resolucion_alto} ({analisis.resolucion_canales} canales)
                      </Typography>
                    </Grid>
                    <Grid size={12}>
                      <Typography variant="body2" color="text.secondary">
                        Tiempo Total:
                      </Typography>
                      <Typography variant="body1">
                        {formatTiempo(analisis.tiempo_total_ms)}
                      </Typography>
                    </Grid>
                  </Grid>

                  {analisis.mensaje_error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {analisis.mensaje_error}
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Columna Derecha - Información Específica del Análisis */}
            <Grid size={{ xs: 12, md: 8 }}>
              {analisis.metadatos_json && (
                <>
                  {/* Información específica según el tipo de análisis */}
                  {analisis.tipo_analisis === 'segmentacion_defectos' && analisis.metadatos_json.resultados?.defectos_segmentadas && (
                    <Card variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          🎯 Segmentación de Defectos
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid size={6}>
                            <Typography variant="body2" color="text.secondary">
                              Defectos Encontrados
                            </Typography>
                            <Typography variant="h4" color="error.main">
                              {analisis.metadatos_json.resultados.defectos_segmentadas.length}
                            </Typography>
                          </Grid>
                          <Grid size={6}>
                            <Typography variant="body2" color="text.secondary">
                              Confianza Promedio
                            </Typography>
                            <Typography variant="h4" color="warning.main">
                              {Math.round((analisis.metadatos_json.resultados.defectos_segmentadas.reduce((acc: number, defecto: any) => acc + defecto.confianza, 0) / analisis.metadatos_json.resultados.defectos_segmentadas.length) * 100)}%
                            </Typography>
                          </Grid>
                          <Grid size={6}>
                            <Typography variant="body2" color="text.secondary">
                              Área Total
                            </Typography>
                            <Typography variant="h6" color="info.main">
                              {analisis.metadatos_json.resultados.defectos_segmentadas.reduce((acc: number, defecto: any) => acc + defecto.area_mascara, 0)} px²
                            </Typography>
                          </Grid>
                          <Grid size={6}>
                            <Typography variant="body2" color="text.secondary">
                              Modelo
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              {analisis.metadatos_json.modelo?.nombre || 'N/A'}
                            </Typography>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  )}

                  {analisis.tipo_analisis === 'segmentacion_piezas' && analisis.metadatos_json.resultados?.piezas_segmentadas && (
                    <Card variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          🧩 Segmentación de Piezas
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid size={6}>
                            <Typography variant="body2" color="text.secondary">
                              Piezas Encontradas
                            </Typography>
                            <Typography variant="h4" color="success.main">
                              {analisis.metadatos_json.resultados.piezas_segmentadas.length}
                            </Typography>
                          </Grid>
                          <Grid size={6}>
                            <Typography variant="body2" color="text.secondary">
                              Confianza Promedio
                            </Typography>
                            <Typography variant="h4" color="warning.main">
                              {Math.round((analisis.metadatos_json.resultados.piezas_segmentadas.reduce((acc: number, pieza: any) => acc + pieza.confianza, 0) / analisis.metadatos_json.resultados.piezas_segmentadas.length) * 100)}%
                            </Typography>
                          </Grid>
                          <Grid size={6}>
                            <Typography variant="body2" color="text.secondary">
                              Área Total
                            </Typography>
                            <Typography variant="h6" color="info.main">
                              {analisis.metadatos_json.resultados.piezas_segmentadas.reduce((acc: number, pieza: any) => acc + pieza.area_mascara, 0)} px²
                            </Typography>
                          </Grid>
                          <Grid size={6}>
                            <Typography variant="body2" color="text.secondary">
                              Modelo
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              {analisis.metadatos_json.modelo?.nombre || 'N/A'}
                            </Typography>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  )}

                  {/* Detalles de Objetos Detectados/Segmentados */}
                  {(analisis.tipo_analisis === 'segmentacion_defectos' || analisis.tipo_analisis === 'segmentacion_piezas') && 
                   analisis.metadatos_json.resultados && (
                    <Card variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          📍 Detalles de {analisis.tipo_analisis === 'segmentacion_defectos' ? 'Defectos' : 'Piezas'}
                        </Typography>
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>ID</TableCell>
                                <TableCell>Clase</TableCell>
                                <TableCell>Confianza</TableCell>
                                <TableCell>Centroide</TableCell>
                                <TableCell>Área</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {(analisis.metadatos_json.resultados.defectos_segmentadas || 
                                analisis.metadatos_json.resultados.piezas_segmentadas || []).map((objeto: any, index: number) => (
                                <TableRow key={objeto.id || index}>
                                  <TableCell>{objeto.id || index + 1}</TableCell>
                                  <TableCell>
                                    <Chip
                                      label={objeto.clase}
                                      size="small"
                                      color={objeto.clase === 'Defecto' ? 'error' : 'success'}
                                    />
                                  </TableCell>
                                  <TableCell>
                                    {Math.round(objeto.confianza * 100)}%
                                  </TableCell>
                                  <TableCell>
                                    ({objeto.centroide?.x || 0}, {objeto.centroide?.y || 0})
                                  </TableCell>
                                  <TableCell>{objeto.area_mascara || objeto.area_bbox || 0}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  )}
                </>
              )}
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DetalleAnalisis;