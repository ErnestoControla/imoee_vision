import React, { useState, useEffect } from 'react';
import { Box, Typography, Button } from '@mui/material';

const DirectImageTest: React.FC = () => {
  const [imageData, setImageData] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadImage = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 Loading image from miniatura endpoint...');
      const response = await fetch('http://localhost:8000/api/analisis/imagenes/miniatura/14/');
      console.log('📡 Response status:', response.status);
      console.log('📡 Response headers:', response.headers);
      
      const data = await response.json();
      console.log('📦 Response data:', data);
      console.log('📦 Thumbnail data type:', typeof data.thumbnail_data);
      console.log('📦 Thumbnail data length:', data.thumbnail_data?.length);
      console.log('📦 First 100 chars:', data.thumbnail_data?.substring(0, 100));
      
      setImageData(data.thumbnail_data);
    } catch (err) {
      console.error('❌ Error loading image:', err);
      setError('Error al cargar la imagen');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadImage();
  }, []);

  if (loading) {
    return <Typography>Cargando imagen directa...</Typography>;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Box sx={{ p: 2, border: '1px solid #ccc', borderRadius: 1 }}>
      <Typography variant="h6" gutterBottom>
        Prueba Directa de Imagen (ID: 14)
      </Typography>
      
      <Button onClick={loadImage} variant="outlined" sx={{ mb: 2 }}>
        Recargar Imagen Directa
      </Button>
      
      {imageData ? (
        <Box>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Datos recibidos: {imageData.length} caracteres
          </Typography>
          <img
            src={`data:image/png;base64,${imageData}`}
            alt="Imagen directa del análisis"
            style={{
              width: '200px',
              height: '200px',
              objectFit: 'contain',
              display: 'block',
              borderRadius: '4px',
              backgroundColor: '#ffffff',
              border: '3px solid #ff0000',
            }}
            onLoad={() => console.log('✅ Direct image loaded successfully')}
            onError={(e) => console.error('❌ Direct image load error:', e)}
          />
          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
            Base64: {imageData.substring(0, 50)}...
          </Typography>
        </Box>
      ) : (
        <Typography>No hay datos de imagen</Typography>
      )}
    </Box>
  );
};

export default DirectImageTest;
