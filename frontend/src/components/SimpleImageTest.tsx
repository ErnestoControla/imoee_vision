import React, { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';

const SimpleImageTest: React.FC = () => {
  const [imageData, setImageData] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadImage = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch('http://localhost:8000/api/analisis/imagenes/test/');
        const data = await response.json();
        
        console.log('Simple test response:', data);
        setImageData(data.thumbnail_data);
      } catch (err) {
        console.error('Error loading image:', err);
        setError('Error al cargar la imagen');
      } finally {
        setLoading(false);
      }
    };

    loadImage();
  }, []);

  if (loading) {
    return <Typography>Cargando...</Typography>;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Box sx={{ p: 2, border: '1px solid #ccc', borderRadius: 1 }}>
      <Typography variant="h6" gutterBottom>
        Prueba Simple de Imagen
      </Typography>
      
      {imageData ? (
        <Box>
          <img
            src={`data:image/png;base64,${imageData}`}
            alt="Imagen de prueba"
            style={{
              width: '180px',
              height: '180px',
              objectFit: 'contain',
              display: 'block',
              borderRadius: '4px',
              backgroundColor: '#ffffff',
              border: '2px solid #ff0000',
            }}
            onLoad={() => console.log('✅ Simple image loaded successfully')}
            onError={(e) => console.error('❌ Simple image load error:', e)}
          />
          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
            Longitud: {imageData.length} caracteres
          </Typography>
        </Box>
      ) : (
        <Typography>No hay datos de imagen</Typography>
      )}
    </Box>
  );
};

export default SimpleImageTest;
