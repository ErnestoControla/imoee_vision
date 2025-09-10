import React, { useState } from 'react';
import { Box, Typography, Button, Alert } from '@mui/material';
import API from '../api/axios';

const TestColorComponent: React.FC = () => {
  const [imageData, setImageData] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testColors = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 Probando colores BGR...');
      
      const response = await API.get('analisis/imagenes/test-camera/');
      const data = response.data;
      
      console.log('📦 Respuesta recibida:', data);
      
      if (data && data.thumbnail_data) {
        const fullDataUrl = `data:image/jpeg;base64,${data.thumbnail_data}`;
        console.log('✅ Imagen de prueba de colores cargada correctamente');
        setImageData(fullDataUrl);
      } else {
        setError('No se encontró imagen de prueba de colores');
      }
    } catch (err) {
      console.error('❌ Error cargando imagen de prueba de colores:', err);
      if (err.response) {
        console.error('❌ Status:', err.response.status);
        console.error('❌ Data:', err.response.data);
        setError(`Error ${err.response.status}: ${err.response.data?.detail || err.response.data?.error || 'Error desconocido'}`);
      } else if (err.request) {
        console.error('❌ Request:', err.request);
        setError('Error de conexión con el servidor');
      } else {
        console.error('❌ Error:', err.message);
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={2} border="1px solid #ccc" borderRadius={1} m={2}>
      <Typography variant="h6" gutterBottom>
        Prueba de Colores BGR
      </Typography>
      
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Esta imagen de prueba tiene colores conocidos en formato BGR:
        <br />• Azul (canal B=255)
        <br />• Verde (canal G=255) 
        <br />• Rojo (canal R=255)
        <br />
        <strong>Si los colores se ven correctos, el problema está en el procesamiento de imágenes reales.</strong>
      </Typography>
      
      <Button 
        variant="contained" 
        onClick={testColors} 
        disabled={loading}
        sx={{ mb: 2 }}
      >
        {loading ? 'Cargando...' : 'Probar Colores BGR'}
      </Button>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {imageData && (
        <Box>
          <Typography variant="body2" color="success" gutterBottom>
            ✅ Imagen de prueba de colores cargada correctamente
          </Typography>
          <img
            src={imageData}
            alt="Imagen de prueba de colores BGR"
            style={{
              width: '200px',
              height: '200px',
              border: '1px solid #ccc',
              borderRadius: '4px',
            }}
            onLoad={() => console.log('✅ Imagen de colores renderizada en el DOM')}
            onError={(e) => {
              console.error('❌ Error renderizando imagen de colores:', e);
              setError('Error al mostrar la imagen de colores');
            }}
          />
        </Box>
      )}
    </Box>
  );
};

export default TestColorComponent;
