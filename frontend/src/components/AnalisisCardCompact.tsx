import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Schedule,
} from '@mui/icons-material';
import type { AnalisisCopleList } from '../api/analisis';
import dayjs from 'dayjs';
import ImagenProcesada from './ImagenProcesada';

interface AnalisisCardCompactProps {
  analisis: AnalisisCopleList;
  onView?: (id: number) => void;
}

const AnalisisCardCompact: React.FC<AnalisisCardCompactProps> = ({
  analisis,
  onView,
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

  return (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4,
        }
      }}
      onClick={() => onView && onView(analisis.id)}
    >
      <CardContent sx={{ p: 2, flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Imagen compacta */}
        <Box mb={2} sx={{ height: 120, overflow: 'hidden', borderRadius: 1 }}>
          <ImagenProcesada
            analisisId={analisis.id}
            showThumbnail={true}
            width={200}
            height={120}
          />
        </Box>

        {/* Información compacta */}
        <Box flex={1}>
          <Typography variant="body2" fontWeight="bold" noWrap>
            {analisis.id_analisis}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {dayjs(analisis.timestamp_procesamiento).format('DD/MM HH:mm')}
          </Typography>
          
          <Box mt={1}>
            <Chip
              icon={getEstadoIcon(analisis.estado)}
              label={analisis.estado}
              color={getEstadoColor(analisis.estado) as any}
              size="small"
              sx={{ fontSize: '0.7rem' }}
            />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default AnalisisCardCompact;
