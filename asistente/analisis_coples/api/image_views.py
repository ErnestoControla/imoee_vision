# analisis_coples/api/image_views.py

from django.http import HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import os
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import logging

from ..models import AnalisisCople
from ..resultados_models import ResultadoClasificacion, DeteccionPieza, DeteccionDefecto

logger = logging.getLogger(__name__)


def get_processed_image(request, analisis_id):
    """
    Obtiene la imagen procesada con los resultados superpuestos
    """
    try:
        # Obtener el análisis
        analisis = AnalisisCople.objects.get(id=analisis_id)
        
        # PRIMERO: Intentar usar la imagen procesada guardada
        if analisis.imagen_procesada and analisis.imagen_procesada.name:
            try:
                logger.info(f"🖼️ [DEBUG] Intentando cargar imagen procesada guardada: {analisis.imagen_procesada.name}")
                
                # Leer la imagen procesada guardada
                with analisis.imagen_procesada.open('rb') as f:
                    image_bytes = f.read()
                
                # Convertir a base64
                import base64
                image_data = base64.b64encode(image_bytes).decode('utf-8')
                
                logger.info(f"✅ [DEBUG] Imagen procesada cargada exitosamente desde archivo guardado")
                
                # Devolver la imagen como base64
                import json
                return HttpResponse(
                    json.dumps({
                        'image_data': image_data,
                        'analisis_id': analisis.id_analisis,
                        'timestamp': analisis.timestamp_procesamiento.isoformat(),
                        'source': 'saved_processed_image'
                    }),
                    content_type='application/json'
                )
                
            except Exception as e:
                logger.warning(f"⚠️ [DEBUG] Error cargando imagen procesada guardada: {e}")
                logger.info(f"🔄 [DEBUG] Fallback a generación desde datos de BD")
        
        # FALLBACK: Generar imagen procesada desde datos de BD
        logger.info(f"🎨 [DEBUG] Generando imagen procesada desde datos de BD...")
        image_data = generate_processed_image(analisis)
        
        if image_data is None:
            import json
            return HttpResponse(
                json.dumps({'error': 'No hay imagen real disponible para este análisis'}),
                content_type='application/json',
                status=404
            )
        
        # Devolver la imagen como base64
        import json
        return HttpResponse(
            json.dumps({
                'image_data': image_data,
                'analisis_id': analisis.id_analisis,
                'timestamp': analisis.timestamp_procesamiento.isoformat(),
                'source': 'generated_from_db'
            }),
            content_type='application/json'
        )
        
    except AnalisisCople.DoesNotExist:
        import json
        return HttpResponse(
            json.dumps({'error': 'Análisis no encontrado'}),
            content_type='application/json',
            status=404
        )
    except Exception as e:
        logger.error(f"Error generando imagen procesada: {e}")
        import json
        return HttpResponse(
            json.dumps({'error': f'Error interno: {str(e)}'}),
            content_type='application/json',
            status=500
        )


def generate_processed_image(analisis: AnalisisCople) -> str:
    """
    Genera una imagen procesada con los resultados superpuestos
    """
    try:
        # Intentar cargar la imagen real del análisis
        image = None
        try:
            # Buscar la imagen real en los metadatos
            if analisis.metadatos_json and 'frame' in analisis.metadatos_json:
                frame_data = analisis.metadatos_json['frame']
                
                # Verificar si es base64 (string) o array de numpy (list)
                if isinstance(frame_data, str):
                    # Es base64, decodificar
                    import base64
                    try:
                        frame_bytes = base64.b64decode(frame_data)
                        # Decodificar los bytes de la imagen JPG a un array de NumPy
                        frame_array = cv2.imdecode(np.frombuffer(frame_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if frame_array is not None:
                            # Asegurar que esté en formato uint8 y RGB
                            if frame_array.dtype != np.uint8:
                                frame_array = frame_array.astype(np.uint8)
                            
                            # Convertir de BGR a RGB para Pillow (cv2.imdecode devuelve BGR)
                            if len(frame_array.shape) == 3 and frame_array.shape[2] == 3:
                                frame_rgb = cv2.cvtColor(frame_array, cv2.COLOR_BGR2RGB)
                            else:
                                frame_rgb = frame_array
                            
                            image = Image.fromarray(frame_rgb)
                            logger.info(f"✅ Imagen real cargada desde base64 y decodificada: {frame_rgb.shape}, dtype: {frame_rgb.dtype}")
                    except Exception as e:
                        logger.warning(f"Error decodificando base64: {e}")
                elif isinstance(frame_data, list):
                    # Es array de numpy serializado como lista
                    try:
                        frame_array = np.array(frame_data, dtype=np.uint8)
                        if len(frame_array.shape) == 3:
                            # La imagen ya está en RGB desde el backend, no convertir
                            image = Image.fromarray(frame_array)
                            logger.info(f"✅ Imagen real cargada desde array: {frame_array.shape}")
                    except Exception as e:
                        logger.warning(f"Error procesando array: {e}")
        except Exception as e:
            logger.warning(f"No se pudo cargar imagen real: {e}")
        
        # Solo usar imagen real - no crear imágenes sintéticas
        if image is None:
            logger.warning(f"⚠️ No hay imagen real disponible para análisis {analisis.id}")
            return None
        
        width, height = image.size
        logger.info(f"✅ Usando imagen real: {width}x{height}")
        
        draw = ImageDraw.Draw(image)
        
        # Intentar cargar una fuente
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # NO dibujar fondo de simulación - usar solo la imagen real
        
        # Obtener resultados de clasificación
        try:
            clasificacion = ResultadoClasificacion.objects.filter(analisis=analisis).first()
            if clasificacion:
                # Dibujar resultado de clasificación
                color = '#4caf50' if clasificacion.clase_predicha == 'Aceptado' else '#f44336'
                draw.rectangle([10, 10, width-10, 60], fill=color, outline='white', width=2)
                
                # Texto de clasificación
                text = f"{clasificacion.clase_predicha} ({clasificacion.confianza:.1%})"
                bbox = draw.textbbox((0, 0), text, font=font_large)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (width - text_width) // 2
                y = (60 - text_height) // 2 + 10
                draw.text((x, y), text, fill='white', font=font_large)
        except Exception as e:
            logger.warning(f"Error dibujando clasificación: {e}")
        
        # Dibujar detecciones de piezas
        try:
            piezas = DeteccionPieza.objects.filter(analisis=analisis)
            for i, pieza in enumerate(piezas):
                # Color para piezas (azul)
                color = '#2196f3'
                
                # Dibujar bounding box
                x1, y1 = int(pieza.bbox_x1), int(pieza.bbox_y1)
                x2, y2 = int(pieza.bbox_x2), int(pieza.bbox_y2)
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                
                # Etiqueta de la pieza
                label = f"Pieza {i+1} ({pieza.confianza:.1%})"
                bbox = draw.textbbox((0, 0), label, font=font_small)
                text_width = bbox[2] - bbox[0]
                draw.rectangle([x1, y1-20, x1+text_width+10, y1], fill=color)
                draw.text((x1+5, y1-18), label, fill='white', font=font_small)
                
                # Centroide
                cx, cy = int(pieza.centroide_x), int(pieza.centroide_y)
                draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill=color)
        except Exception as e:
            logger.warning(f"Error dibujando piezas: {e}")
        
        # Dibujar detecciones de defectos
        try:
            defectos = DeteccionDefecto.objects.filter(analisis=analisis)
            for i, defecto in enumerate(defectos):
                # Color para defectos (rojo)
                color = '#ff9800'
                
                # Dibujar bounding box
                x1, y1 = int(defecto.bbox_x1), int(defecto.bbox_y1)
                x2, y2 = int(defecto.bbox_x2), int(defecto.bbox_y2)
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                
                # Etiqueta del defecto
                label = f"Defecto {i+1} ({defecto.confianza:.1%})"
                bbox = draw.textbbox((0, 0), label, font=font_small)
                text_width = bbox[2] - bbox[0]
                draw.rectangle([x1, y1-20, x1+text_width+10, y1], fill=color)
                draw.text((x1+5, y1-18), label, fill='white', font=font_small)
                
                # Centroide
                cx, cy = int(defecto.centroide_x), int(defecto.centroide_y)
                draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill=color)
        except Exception as e:
            logger.warning(f"Error dibujando defectos: {e}")
        
        # Información del análisis
        info_text = f"ID: {analisis.id_analisis} | {analisis.timestamp_procesamiento.strftime('%H:%M:%S')}"
        draw.text((10, height-30), info_text, fill='#666666', font=font_small)
        
        # Convertir a base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return image_data
        
    except Exception as e:
        logger.error(f"Error generando imagen procesada: {e}")
        return None


def get_analysis_thumbnail(request, analisis_id):
    """
    Obtiene una miniatura de la imagen procesada
    """
    try:
        # Obtener el análisis
        analisis = AnalisisCople.objects.get(id=analisis_id)
        
        # Generar miniatura
        thumbnail_data = generate_thumbnail(analisis)
        
        if thumbnail_data is None:
            return HttpResponse(
                json.dumps({'error': 'No hay imagen real disponible para este análisis'}),
                content_type='application/json',
                status=404
            )
        
        return HttpResponse(
            json.dumps({
                'thumbnail_data': thumbnail_data,
                'analisis_id': analisis.id_analisis
            }),
            content_type='application/json'
        )
    except AnalisisCople.DoesNotExist:
        return HttpResponse(
            json.dumps({'error': 'Análisis no encontrado'}),
            content_type='application/json',
            status=404
        )
    except Exception as e:
        logger.error(f"Error generando miniatura: {e}")
        return HttpResponse(
            json.dumps({'error': f'Error interno: {str(e)}'}),
            content_type='application/json',
            status=500
        )


def test_image(request):
    """Endpoint de prueba para generar una imagen simple"""
    try:
        # Crear una imagen de prueba muy simple
        img = Image.new('RGB', (100, 100), color='red')
        draw = ImageDraw.Draw(img)
        
        # Dibujar un rectángulo azul
        draw.rectangle([20, 20, 80, 80], fill='blue')
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return HttpResponse(
            json.dumps({
                'thumbnail_data': img_base64,
                'analisis_id': 'test_image_123'
            }),
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f"Error generando imagen de prueba: {e}")
        return HttpResponse(
            json.dumps({'error': f'Error generando imagen de prueba: {str(e)}'}),
            content_type='application/json',
            status=500
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_image_auth(request):
    """Endpoint de prueba autenticado para generar una imagen simple"""
    try:
        # Crear una imagen de prueba muy simple
        img = Image.new('RGB', (100, 100), color='green')
        draw = ImageDraw.Draw(img)
        
        # Dibujar un rectángulo rojo
        draw.rectangle([20, 20, 80, 80], fill='red')
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return Response({
            'thumbnail_data': img_base64,
            'analisis_id': 'test_image_auth_123',
            'message': 'Imagen de prueba generada correctamente'
        })
    except Exception as e:
        logger.error(f"Error generando imagen de prueba autenticada: {e}")
        return Response(
            {'error': f'Error generando imagen de prueba: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_camera_preview(request):
    """Endpoint para obtener una previsualización en tiempo real de la cámara"""
    try:
        # Importar el servicio de análisis
        from analisis_coples.services_real import servicio_analisis_real
        
        if not servicio_analisis_real.inicializado:
            return Response(
                {'error': 'Sistema no inicializado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener frame actual de la cámara
        if servicio_analisis_real.sistema_analisis and servicio_analisis_real.sistema_analisis.webcam_fallback:
            # Obtener frame instantáneo
            frame, tiempo_acceso_ms, timestamp = servicio_analisis_real.sistema_analisis.webcam_fallback.obtener_frame_instantaneo()
            
            if frame is None:
                return Response(
                    {'error': 'No se pudo obtener frame de la cámara'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Codificar frame como JPG en BGR (como se hace en el sistema real)
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return Response({
                'preview_data': frame_base64,
                'timestamp': timestamp,
                'tiempo_acceso_ms': tiempo_acceso_ms,
                'frame_shape': str(frame.shape),
                'message': 'Previsualización de cámara obtenida correctamente'
            })
        else:
            return Response(
                {'error': 'Cámara no disponible'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error obteniendo previsualización de cámara: {e}")
        return Response(
            {'error': f'Error obteniendo previsualización: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def generate_thumbnail(analisis: AnalisisCople) -> str:
    """
    Genera una miniatura de la imagen procesada
    """
    try:
        # Intentar cargar la imagen real del análisis
        image = None
        try:
            # Buscar la imagen real en los metadatos
            if analisis.metadatos_json and 'frame' in analisis.metadatos_json:
                frame_data = analisis.metadatos_json['frame']
                
                # Verificar si es base64 (string) o array de numpy (list)
                if isinstance(frame_data, str):
                    # Es base64, decodificar
                    import base64
                    try:
                        frame_bytes = base64.b64decode(frame_data)
                        # Decodificar los bytes de la imagen JPG a un array de NumPy
                        frame_array = cv2.imdecode(np.frombuffer(frame_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if frame_array is not None:
                            # Asegurar que esté en formato uint8 y RGB
                            if frame_array.dtype != np.uint8:
                                frame_array = frame_array.astype(np.uint8)
                            
                            # Convertir de BGR a RGB para Pillow (cv2.imdecode devuelve BGR)
                            if len(frame_array.shape) == 3 and frame_array.shape[2] == 3:
                                frame_rgb = cv2.cvtColor(frame_array, cv2.COLOR_BGR2RGB)
                            else:
                                frame_rgb = frame_array
                            
                            # Redimensionar a miniatura
                            original_image = Image.fromarray(frame_rgb)
                            image = original_image.resize((200, 200), Image.Resampling.LANCZOS)
                            logger.info(f"✅ Miniatura real generada desde base64 y decodificada: {frame_rgb.shape} -> 200x200, dtype: {frame_rgb.dtype}")
                    except Exception as e:
                        logger.warning(f"Error decodificando base64 para miniatura: {e}")
                elif isinstance(frame_data, list):
                    # Es array de numpy serializado como lista
                    try:
                        frame_array = np.array(frame_data, dtype=np.uint8)
                        if len(frame_array.shape) == 3:
                            # La imagen ya está en RGB desde el backend, no convertir
                            # Redimensionar a miniatura
                            original_image = Image.fromarray(frame_array)
                            image = original_image.resize((200, 200), Image.Resampling.LANCZOS)
                            logger.info(f"✅ Miniatura real generada desde array: {frame_array.shape} -> 200x200")
                    except Exception as e:
                        logger.warning(f"Error procesando array para miniatura: {e}")
        except Exception as e:
            logger.warning(f"No se pudo cargar imagen real para miniatura: {e}")
        
        # Solo usar imagen real - no crear miniaturas sintéticas
        if image is None:
            logger.warning(f"⚠️ No hay imagen real disponible para miniatura del análisis {analisis.id}")
            return None
        
        width, height = image.size
        logger.info(f"✅ Usando miniatura real: {width}x{height}")
        
        draw = ImageDraw.Draw(image)
        
        # Intentar cargar una fuente pequeña
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            font = ImageFont.load_default()
        
        # NO dibujar fondo - usar solo la imagen real
        
        # Obtener resultado de clasificación
        try:
            clasificacion = ResultadoClasificacion.objects.filter(analisis=analisis).first()
            if clasificacion:
                # Color según resultado
                color = '#4caf50' if clasificacion.clase_predicha == 'Aceptado' else '#f44336'
                
                # Dibujar resultado
                draw.rectangle([5, 5, width-5, 25], fill=color, outline='white', width=1)
                text = f"{clasificacion.clase_predicha} ({clasificacion.confianza:.0%})"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x, 8), text, fill='white', font=font)
        except Exception as e:
            logger.warning(f"Error dibujando clasificación en miniatura: {e}")
        
        # Dibujar detecciones simplificadas
        try:
            piezas = DeteccionPieza.objects.filter(analisis=analisis)
            for pieza in piezas:
                # Escalar coordenadas a la miniatura
                x1 = int((pieza.bbox_x1 / 640) * width)
                y1 = int((pieza.bbox_y1 / 640) * height)
                x2 = int((pieza.bbox_x2 / 640) * width)
                y2 = int((pieza.bbox_y2 / 640) * height)
                draw.rectangle([x1, y1, x2, y2], outline='#2196f3', width=1)
            
            defectos = DeteccionDefecto.objects.filter(analisis=analisis)
            for defecto in defectos:
                # Escalar coordenadas a la miniatura
                x1 = int((defecto.bbox_x1 / 640) * width)
                y1 = int((defecto.bbox_y1 / 640) * height)
                x2 = int((defecto.bbox_x2 / 640) * width)
                y2 = int((defecto.bbox_y2 / 640) * height)
                draw.rectangle([x1, y1, x2, y2], outline='#ff9800', width=1)
        except Exception as e:
            logger.warning(f"Error dibujando detecciones en miniatura: {e}")
        
        # Convertir a base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        thumbnail_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return thumbnail_data
        
    except Exception as e:
        logger.error(f"Error generando miniatura: {e}")
        return None
