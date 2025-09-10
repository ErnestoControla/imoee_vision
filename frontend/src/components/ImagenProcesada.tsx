import React, { useState, useEffect } from 'react';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import API from '../api/axios';

interface ImagenProcesadaProps {
  analisisId: number;
  showThumbnail?: boolean;
  width?: number;
  height?: number;
}

const ImagenProcesada: React.FC<ImagenProcesadaProps> = ({ 
  analisisId, 
  showThumbnail = false,
  width = 300,
  height = 300
}) => {
  const [imageData, setImageData] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadImage = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Usar el endpoint de miniatura para las tarjetas, imagen completa para detalles
        const endpoint = showThumbnail 
          ? `analisis/imagenes/miniatura/${analisisId}/`
          : `analisis/imagenes/procesada/${analisisId}/`;
        
        console.log(`🔄 Cargando imagen desde: ${endpoint}`);
        
        const response = await API.get(endpoint);
        const data = await response.data;
        
        console.log(`📦 Respuesta recibida:`, data);
        
        // El endpoint de miniatura devuelve 'thumbnail_data', el de procesada devuelve 'image_data'
        const imageField = showThumbnail ? 'thumbnail_data' : 'image_data';
        
        if (data && data[imageField]) {
          const rawData = data[imageField];
          console.log(`📊 Datos de imagen: ${rawData.length} caracteres, primeros 50: ${rawData.substring(0, 50)}`);
          
          // Verificar si ya tiene el prefijo data: o si es solo base64
          let fullDataUrl;
          if (rawData.startsWith('data:')) {
            fullDataUrl = rawData;
            console.log(`✅ Imagen ya tiene prefijo data:`);
          } else {
            // Agregar el prefijo correcto según el formato
            // El backend devuelve PNG, no JPG
            fullDataUrl = `data:image/png;base64,${rawData}`;
            console.log(`✅ Agregando prefijo data:image/png;base64,`);
          }
          
          console.log(`✅ Imagen cargada correctamente, tamaño total: ${fullDataUrl.length} caracteres`);
          setImageData(fullDataUrl);
        } else {
          console.error(`❌ No se encontró el campo ${imageField} en la respuesta`);
          setError('No se encontró imagen procesada');
        }
      } catch (err) {
        console.error('❌ Error cargando imagen procesada:', err);
        setError('Error al cargar la imagen');
      } finally {
        setLoading(false);
      }
    };

    if (analisisId) {
      loadImage();
    }
  }, [analisisId, showThumbnail]);

  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        width={width} 
        height={height}
        border="1px solid #e0e0e0"
        borderRadius={1}
        bgcolor="#f5f5f5"
      >
        <CircularProgress size={24} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        width={width} 
        height={height}
        border="1px solid #e0e0e0"
        borderRadius={1}
        bgcolor="#f5f5f5"
      >
        <Alert severity="warning" sx={{ fontSize: '0.8rem' }}>
          {error}
        </Alert>
      </Box>
    );
  }

  if (!imageData) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        width={width} 
        height={height}
        border="1px solid #e0e0e0"
        borderRadius={1}
        bgcolor="#f5f5f5"
      >
        <Typography variant="body2" color="text.secondary">
          Sin imagen
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <img
        src={imageData}
        alt={`Imagen procesada del análisis ${analisisId}`}
        style={{
          width: showThumbnail ? '100px' : `${width}px`,
          height: showThumbnail ? '100px' : `${height}px`,
          objectFit: 'cover',
          borderRadius: '8px',
          border: '1px solid #e0e0e0',
          display: 'block',
        }}
        onLoad={() => console.log('✅ Imagen procesada cargada correctamente en el DOM')}
        onError={(e) => {
          console.error('❌ Error cargando imagen procesada en el DOM:', e);
          console.error('❌ URL de la imagen:', imageData.substring(0, 100) + '...');
          setError('Error al mostrar la imagen');
        }}
      />
    </Box>
  );
};

export default ImagenProcesada;