import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, CircularProgress, Alert, Card, CardContent } from '@mui/material';
import { Videocam, VideocamOff } from '@mui/icons-material';
import API from '../api/axios';

interface CameraPreviewProps {
  isActive?: boolean;
  width?: number;
  height?: number;
  refreshInterval?: number;
}

const CameraPreview: React.FC<CameraPreviewProps> = ({ 
  isActive = false,
  width = 400,
  height = 300,
  refreshInterval = 200 // 5 FPS para previsualización
}) => {
  const [previewData, setPreviewData] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchPreview = async () => {
    if (!isActive) return;
    
    try {
      setError(null);
      const response = await API.get('/analisis/imagenes/preview/');
      
      if (response.data && response.data.preview_data) {
        setPreviewData(response.data.preview_data);
        setIsStreaming(true);
      } else {
        setError('No se pudo obtener la previsualización');
        setIsStreaming(false);
      }
    } catch (error: any) {
      console.error('Error obteniendo previsualización:', error);
      setError(error.response?.data?.error || 'Error obteniendo previsualización');
      setIsStreaming(false);
    }
  };

  useEffect(() => {
    if (isActive) {
      setLoading(true);
      // Obtener primera imagen inmediatamente
      fetchPreview().finally(() => setLoading(false));
      
      // Configurar intervalo para actualizaciones
      intervalRef.current = setInterval(() => {
        fetchPreview();
      }, refreshInterval);
    } else {
      // Limpiar intervalo cuando se desactiva
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      setPreviewData(null);
      setIsStreaming(false);
      setError(null);
    }

    // Cleanup al desmontar
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isActive, refreshInterval]);

  const getPreviewImageSrc = () => {
    if (previewData) {
      return `data:image/jpeg;base64,${previewData}`;
    }
    return null;
  };

  return (
    <Card sx={{ width: width, height: height + 60 }}>
      <CardContent sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          {isStreaming ? (
            <Videocam color="success" />
          ) : (
            <VideocamOff color="disabled" />
          )}
          <Typography variant="h6" component="h3">
            Previsualización de Cámara
          </Typography>
        </Box>

        <Box 
          sx={{ 
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f5f5f5',
            borderRadius: 1,
            overflow: 'hidden',
            position: 'relative',
            minHeight: height
          }}
        >
          {loading && (
            <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
              <CircularProgress size={40} />
              <Typography variant="body2" color="text.secondary">
                Iniciando cámara...
              </Typography>
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ maxWidth: '90%' }}>
              {error}
            </Alert>
          )}

          {!loading && !error && previewData && (
            <img
              src={getPreviewImageSrc() || ''}
              alt="Previsualización de cámara"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                borderRadius: '4px'
              }}
            />
          )}

          {!loading && !error && !previewData && isActive && (
            <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
              <VideocamOff sx={{ fontSize: 48, color: 'text.disabled' }} />
              <Typography variant="body2" color="text.secondary">
                Esperando señal de cámara...
              </Typography>
            </Box>
          )}

          {!isActive && (
            <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
              <VideocamOff sx={{ fontSize: 48, color: 'text.disabled' }} />
              <Typography variant="body2" color="text.secondary">
                Cámara inactiva
              </Typography>
            </Box>
          )}
        </Box>

        {isStreaming && (
          <Typography variant="caption" color="success.main" sx={{ mt: 1, textAlign: 'center' }}>
            ● En vivo
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default CameraPreview;
