import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Visibility,
  ChevronLeft,
  ChevronRight,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import type { AnalisisCopleList } from '../api/analisis';
import AnalisisCardCompact from './AnalisisCardCompact';

interface AnalisisRecientesPorTipoProps {
  analisis: AnalisisCopleList[];
  onView: (id: number) => void;
}

interface AnalisisPorTipo {
  tipo: string;
  titulo: string;
  color: string;
  analisis: AnalisisCopleList[];
}

const AnalisisRecientesPorTipo: React.FC<AnalisisRecientesPorTipoProps> = ({
  analisis,
  onView,
}) => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Agrupar análisis por tipo
  const analisisPorTipo: AnalisisPorTipo[] = [
    {
      tipo: 'clasificacion',
      titulo: 'Clasificación de Defectos',
      color: '#4CAF50',
      analisis: analisis.filter(a => a.tipo_analisis === 'clasificacion').slice(0, 6),
    },
    {
      tipo: 'deteccion_piezas',
      titulo: 'Detección de Piezas',
      color: '#2196F3',
      analisis: analisis.filter(a => a.tipo_analisis === 'deteccion_piezas').slice(0, 6),
    },
    {
      tipo: 'deteccion_defectos',
      titulo: 'Detección de Defectos',
      color: '#FF9800',
      analisis: analisis.filter(a => a.tipo_analisis === 'deteccion_defectos').slice(0, 6),
    },
    {
      tipo: 'segmentacion_defectos',
      titulo: 'Segmentación de Defectos',
      color: '#9C27B0',
      analisis: analisis.filter(a => a.tipo_analisis === 'segmentacion_defectos').slice(0, 6),
    },
    {
      tipo: 'segmentacion_piezas',
      titulo: 'Segmentación de Piezas',
      color: '#E91E63',
      analisis: analisis.filter(a => a.tipo_analisis === 'segmentacion_piezas').slice(0, 6),
    },
  ];

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case 'clasificacion':
        return '🧠';
      case 'deteccion_piezas':
        return '🎯';
      case 'deteccion_defectos':
        return '🔍';
      case 'segmentacion_defectos':
        return '🎨';
      case 'segmentacion_piezas':
        return '🖼️';
      default:
        return '📊';
    }
  };

  return (
    <Box>
      <Typography 
        variant="h5" 
        gutterBottom 
        sx={{ 
          color: 'white', 
          fontWeight: 'bold',
          mb: 3,
          textAlign: 'center'
        }}
      >
        Análisis Recientes
      </Typography>

      <Grid container spacing={3}>
        {analisisPorTipo.map((grupo) => (
          <Grid item xs={12} key={grupo.tipo}>
            <Card 
              sx={{ 
                background: `linear-gradient(135deg, ${grupo.color}20 0%, ${grupo.color}10 100%)`,
                border: `1px solid ${grupo.color}40`,
                borderRadius: 2,
                overflow: 'hidden'
              }}
            >
              <CardContent sx={{ p: 2 }}>
                {/* Header del tipo */}
                <Box 
                  display="flex" 
                  alignItems="center" 
                  justifyContent="space-between"
                  mb={2}
                >
                  <Box display="flex" alignItems="center" gap={1}>
                    <Typography variant="h6" sx={{ fontSize: '1.2rem' }}>
                      {getTipoIcon(grupo.tipo)}
                    </Typography>
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        color: grupo.color,
                        fontWeight: 'bold',
                        fontSize: '1.1rem'
                      }}
                    >
                      {grupo.titulo}
                    </Typography>
                    <Chip 
                      label={grupo.analisis.length}
                      size="small"
                      sx={{ 
                        backgroundColor: grupo.color,
                        color: 'white',
                        fontWeight: 'bold'
                      }}
                    />
                  </Box>
                  
                  {grupo.analisis.length > 3 && (
                    <Box display="flex" gap={1}>
                      <Tooltip title="Ver más">
                        <IconButton 
                          size="small"
                          sx={{ color: grupo.color }}
                        >
                          <ChevronRight />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  )}
                </Box>

                {/* Grid de análisis */}
                {grupo.analisis.length > 0 ? (
                  <Grid container spacing={2}>
                    {grupo.analisis.slice(0, 3).map((analisisItem) => (
                      <Grid item xs={12} sm={6} md={4} key={analisisItem.id}>
                        <AnalisisCardCompact
                          analisis={analisisItem}
                          onView={onView}
                        />
                      </Grid>
                    ))}
                    
                    {/* Mostrar indicador si hay más análisis */}
                    {grupo.analisis.length > 3 && (
                      <Grid item xs={12} sm={6} md={4}>
                        <Card 
                          sx={{ 
                            height: '100%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: `linear-gradient(135deg, ${grupo.color}15 0%, ${grupo.color}05 100%)`,
                            border: `2px dashed ${grupo.color}40`,
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            '&:hover': {
                              background: `linear-gradient(135deg, ${grupo.color}25 0%, ${grupo.color}15 100%)`,
                              border: `2px dashed ${grupo.color}60`,
                            }
                          }}
                          onClick={() => {
                            // Filtrar por tipo específico
                            navigate('/analisis', { 
                              state: { filtroTipo: grupo.tipo } 
                            });
                          }}
                        >
                          <Box textAlign="center" p={2}>
                            <Typography 
                              variant="h4" 
                              sx={{ color: grupo.color, mb: 1 }}
                            >
                              +{grupo.analisis.length - 3}
                            </Typography>
                            <Typography 
                              variant="body2" 
                              sx={{ color: grupo.color, fontWeight: 'bold' }}
                            >
                              Ver más
                            </Typography>
                          </Box>
                        </Card>
                      </Grid>
                    )}
                  </Grid>
                ) : (
                  <Box 
                    display="flex" 
                    alignItems="center" 
                    justifyContent="center"
                    minHeight={120}
                    sx={{ 
                      background: `linear-gradient(135deg, ${grupo.color}10 0%, ${grupo.color}05 100%)`,
                      borderRadius: 1,
                      border: `1px dashed ${grupo.color}30`
                    }}
                  >
                    <Box textAlign="center">
                      <Typography 
                        variant="h4" 
                        sx={{ color: grupo.color, mb: 1 }}
                      >
                        {getTipoIcon(grupo.tipo)}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ color: grupo.color }}
                      >
                        No hay análisis de este tipo
                      </Typography>
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default AnalisisRecientesPorTipo;
