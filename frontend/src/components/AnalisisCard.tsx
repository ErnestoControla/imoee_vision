// src/components/AnalisisCard.tsx
import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Chip,
  Box,
  LinearProgress,
  IconButton,
  Tooltip,
  Button,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Schedule,
  Visibility,
  Download,
} from '@mui/icons-material';
import type { AnalisisCopleList } from '../api/analisis';
import dayjs from 'dayjs';
import ImagenProcesada from './ImagenProcesada';

interface AnalisisCardProps {
  analisis: AnalisisCopleList;
  onView?: (id: number) => void;
  onDownload?: (id: number) => void;
  compact?: boolean;
}

const AnalisisCard: React.FC<AnalisisCardProps> = ({
  analisis,
  onView,
  onDownload,
  compact = false,
}) => {
  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'completado':
        return 'success';
      case 'error':
        return 'error';
      case 'procesando':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getEstadoIcon = (estado: string) => {
    switch (estado) {
      case 'completado':
        return <CheckCircle />;
      case 'error':
        return <Error />;
      case 'procesando':
        return <Schedule />;
      default:
        return <Schedule />;
    }
  };

  const getTipoAnalisisLabel = (tipo: string) => {
    const labels: { [key: string]: string } = {
      completo: 'Análisis Completo',
      clasificacion: 'Solo Clasificación',
      deteccion_piezas: 'Detección de Piezas',
      deteccion_defectos: 'Detección de Defectos',
      segmentacion_defectos: 'Segmentación de Defectos',
      segmentacion_piezas: 'Segmentación de Piezas',
    };
    return labels[tipo] || tipo;
  };

  const formatTiempo = (ms: number) => {
    if (ms < 1000) {
      return `${ms.toFixed(0)}ms`;
    }
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="h6" component="div" noWrap>
              {analisis.id_analisis}
            </Typography>
            <Chip
              icon={getEstadoIcon(analisis.estado)}
              label={analisis.estado}
              color={getEstadoColor(analisis.estado) as any}
              size="small"
            />
          </Box>
        }
        subheader={
          <Box>
            <Typography variant="body2" color="text.secondary">
              {dayjs(analisis.timestamp_procesamiento).format('DD/MM/YYYY HH:mm:ss')}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {analisis.usuario_nombre} • {analisis.configuracion_nombre}
            </Typography>
          </Box>
        }
        action={
          <Box display="flex" gap={1} alignItems="center">
            {onView && (
              <Tooltip title="Ver detalles">
                <IconButton
                  size="medium"
        onClick={() => onView(analisis.id)}
                  color="primary"
                  sx={{ 
                    backgroundColor: 'rgba(25, 118, 210, 0.1)',
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.2)',
                    }
                  }}
                >
                  <Visibility />
                </IconButton>
              </Tooltip>
            )}
            {onDownload && analisis.estado === 'completado' && (
              <Tooltip title="Descargar resultados">
                <IconButton
                  size="medium"
                  onClick={() => onDownload(analisis.id)}
                  color="secondary"
                  sx={{ 
                    backgroundColor: 'rgba(156, 39, 176, 0.1)',
                    '&:hover': {
                      backgroundColor: 'rgba(156, 39, 176, 0.2)',
                    }
                  }}
                >
                  <Download />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        }
      />
      <CardContent sx={{ flexGrow: 1 }}>
        <Box mb={2}>
          <Chip
            label={getTipoAnalisisLabel(analisis.tipo_analisis)}
            variant="outlined"
            size="small"
          />
        </Box>

        {analisis.estado === 'completado' && (
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Imagen Procesada:
            </Typography>
            <ImagenProcesada 
              analisisId={analisis.id} 
              showThumbnail={true}
            />
          </Box>
        )}

        {analisis.estado === 'completado' && analisis.clase_predicha && (
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Resultado de Clasificación:
            </Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <Chip
                label={analisis.clase_predicha}
                color={analisis.clase_predicha === 'Aceptado' ? 'success' : 'error'}
                size="small"
              />
              {analisis.confianza && (
                <Typography variant="body2" color="text.secondary">
                  ({Math.round(analisis.confianza * 100)}%)
                </Typography>
              )}
            </Box>
          </Box>
        )}

        {analisis.estado === 'procesando' && (
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Procesando...
            </Typography>
            <LinearProgress />
          </Box>
        )}

        {analisis.estado === 'error' && analisis.mensaje_error && (
          <Box mb={2}>
            <Typography variant="body2" color="error" gutterBottom>
              Error: {analisis.mensaje_error}
            </Typography>
          </Box>
        )}

        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="body2" color="text.secondary">
            Tiempo: {formatTiempo(analisis.tiempo_total_ms)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {dayjs(analisis.timestamp_captura).format('HH:mm:ss')}
          </Typography>
        </Box>

        {/* Botón de Ver Detalles más visible */}
        {onView && (
          <Box display="flex" justifyContent="center">
            <Button
              variant="outlined"
              size="small"
              startIcon={<Visibility />}
        onClick={() => onView(analisis.id)}
              sx={{
                borderColor: 'primary.main',
                color: 'primary.main',
                '&:hover': {
                  borderColor: 'primary.dark',
                  backgroundColor: 'primary.light',
                  color: 'primary.dark',
                }
              }}
            >
              Ver Detalles
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default AnalisisCard;
