# analisis_coples/services_real.py

"""
Servicio real para el sistema de análisis de coples integrado con Django
Versión que usa la cámara real y el sistema de análisis completo
"""

import os
import sys
import time
import uuid
import logging
import numpy as np
import cv2
import base64
from datetime import datetime
from typing import Dict, Any, Optional
import json

from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Importar modelos Django
from .models import ConfiguracionSistema, AnalisisCople
from .resultados_models import (
    ResultadoClasificacion,
    DeteccionPieza,
    DeteccionDefecto,
    SegmentacionDefecto,
    SegmentacionPieza
)

# Importar OpenCV para captura de webcam
import cv2

# Importar sistema real de análisis
from .modules.analysis_system import SistemaAnalisisIntegrado
from .modules.capture.webcam_fallback import WebcamFallback, detectar_mejor_webcam
from .expo_config import WebcamConfig, ModelsConfig

logger = logging.getLogger(__name__)


class ServicioAnalisisCoplesReal:
    """
    Servicio Django que usa el sistema real de análisis de coples
    """
    
    def __init__(self):
        self.inicializado = False
        self.configuracion_activa = None
        self.sistema_analisis = SistemaAnalisisIntegrado()
        self.usando_webcam = False
        
        # Intentar cargar la configuración activa automáticamente
        self._cargar_configuracion_activa()
    
    def _cargar_configuracion_activa(self):
        """Carga la configuración activa de la base de datos"""
        try:
            self.configuracion_activa = ConfiguracionSistema.objects.filter(activa=True).first()
            if self.configuracion_activa:
                logger.info(f"Configuración activa cargada: {self.configuracion_activa.nombre}")
            else:
                logger.warning("No hay configuración activa en la base de datos")
        except Exception as e:
            logger.error(f"Error cargando configuración activa: {e}")
            self.configuracion_activa = None
    
    def inicializar_sistema(self, configuracion_id: Optional[int] = None) -> bool:
        """
        Inicializa el sistema de análisis con la configuración especificada
        
        Args:
            configuracion_id: ID de la configuración a usar. Si es None, usa la activa
            
        Returns:
            bool: True si se inicializó correctamente
        """
        try:
            # Obtener configuración
            if configuracion_id:
                self.configuracion_activa = ConfiguracionSistema.objects.get(id=configuracion_id)
            else:
                self.configuracion_activa = ConfiguracionSistema.objects.filter(activa=True).first()
            
            if not self.configuracion_activa:
                logger.error("No hay configuración activa disponible")
                return False
            
            # Inicializar sistema de análisis real
            if self.sistema_analisis.inicializar():
                self.inicializado = True
                self.usando_webcam = self.sistema_analisis.usando_webcam
                logger.info(f"Sistema de análisis REAL inicializado con configuración: {self.configuracion_activa.nombre}")
                logger.info(f"Usando: {'Webcam' if self.usando_webcam else 'Cámara GigE'}")
                return True
            else:
                logger.error("Error al inicializar el sistema de análisis REAL.")
                return False
            
        except Exception as e:
            logger.error(f"Error inicializando sistema REAL: {e}")
            return False
    
    def _inicializar_webcam(self) -> bool:
        """Inicializa la webcam usando OpenCV"""
        try:
            # Detectar webcam disponible
            webcam_id = self._detectar_webcam()
            if webcam_id is None:
                logger.error("No se encontraron webcams disponibles")
                return False
            
            logger.info(f"📷 Inicializando webcam en dispositivo {webcam_id}")
            
            # Crear objeto VideoCapture
            self.cap = cv2.VideoCapture(webcam_id)
            self.device_id = webcam_id
            
            if not self.cap.isOpened():
                logger.error(f"❌ No se pudo abrir la webcam en dispositivo {webcam_id}")
                return False
            
            # Configurar resolución
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Probar captura
            ret, frame = self.cap.read()
            if not ret or frame is None:
                logger.error("❌ Error en captura de prueba")
                return False
            
            # Obtener resolución real
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"✅ Webcam configurada:")
            logger.info(f"   📐 Resolución: {width}x{height}")
            logger.info(f"   🎬 FPS: {fps:.1f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando webcam: {e}")
            return False
    
    def _detectar_webcam(self) -> Optional[int]:
        """Detecta la mejor webcam disponible"""
        logger.info("🔍 Buscando webcams disponibles...")
        
        # Probar hasta 5 dispositivos
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # Intentar leer un frame para verificar que funciona
                ret, frame = cap.read()
                if ret and frame is not None:
                    logger.info(f"✅ Webcam encontrada en dispositivo {i}")
                    cap.release()
                    return i
                cap.release()
            else:
                cap.release()
        
        logger.error("❌ No se encontraron webcams disponibles")
        return None
    
    def realizar_analisis_completo(self, usuario=None) -> Dict[str, Any]:
        """
        Realiza un análisis completo de cople usando la cámara real
        
        Args:
            usuario: Usuario que realiza el análisis
            
        Returns:
            Dict con el resultado del análisis
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            # Generar ID único para el análisis
            id_analisis = f"analisis_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            logger.info(f"🔄 [DEBUG] Iniciando análisis completo: {id_analisis}")
            logger.info(f"🔄 [DEBUG] Sistema inicializado: {self.inicializado}")
            logger.info(f"🔄 [DEBUG] Configuración activa: {self.configuracion_activa.nombre if self.configuracion_activa else 'None'}")
            
            # Capturar imagen de la cámara
            logger.info(f"📸 [DEBUG] Iniciando captura de imagen...")
            imagen_capturada = self._capturar_imagen()
            if imagen_capturada is None:
                logger.error(f"❌ [DEBUG] Error: No se pudo capturar imagen de la cámara")
                return {"error": "No se pudo capturar imagen de la cámara"}
            
            logger.info(f"📸 [DEBUG] Imagen capturada exitosamente:")
            logger.info(f"   📐 Shape: {imagen_capturada.shape}")
            logger.info(f"   🎨 Dtype: {imagen_capturada.dtype}")
            logger.info(f"   📊 Min/Max: {imagen_capturada.min()}/{imagen_capturada.max()}")
            
            # Crear registro de análisis en la base de datos
            analisis_db = AnalisisCople.objects.create(
                id_analisis=id_analisis,
                timestamp_captura=timezone.now(),
                tipo_analisis='completo',
                estado='procesando',
                configuracion=self.configuracion_activa,
                usuario=usuario,
                archivo_imagen=f"real_{id_analisis}.jpg",
                archivo_json=f"real_{id_analisis}.json",
                resolucion_ancho=imagen_capturada.shape[1],
                resolucion_alto=imagen_capturada.shape[0],
                resolucion_canales=imagen_capturada.shape[2] if len(imagen_capturada.shape) > 2 else 1,
                tiempo_captura_ms=50.0,
                tiempo_clasificacion_ms=0.0,
                tiempo_deteccion_piezas_ms=0.0,
                tiempo_deteccion_defectos_ms=0.0,
                tiempo_segmentacion_defectos_ms=0.0,
                tiempo_segmentacion_piezas_ms=0.0,
                tiempo_total_ms=0.0,
                metadatos_json={}
            )
            
            # Realizar análisis completo usando el sistema real
            logger.info(f"🔬 [DEBUG] Iniciando análisis completo con sistema...")
            resultados = self.sistema_analisis.analisis_completo()
            
            logger.info(f"🔬 [DEBUG] Análisis completado. Resultados recibidos:")
            logger.info(f"   📊 Tipo de resultados: {type(resultados)}")
            logger.info(f"   📋 Claves en resultados: {list(resultados.keys()) if isinstance(resultados, dict) else 'No es dict'}")
            
            # Debug de cada sección de resultados
            if isinstance(resultados, dict):
                for clave, valor in resultados.items():
                    if isinstance(valor, list):
                        logger.info(f"   📝 {clave}: Lista con {len(valor)} elementos")
                        if len(valor) > 0:
                            logger.info(f"      🎯 Primer elemento tipo: {type(valor[0])}")
                    elif isinstance(valor, dict):
                        logger.info(f"   📝 {clave}: Dict con claves: {list(valor.keys())}")
                    else:
                        logger.info(f"   📝 {clave}: {type(valor)} = {valor}")
            
            # Procesar resultados y guardar en base de datos
            logger.info(f"💾 [DEBUG] Iniciando procesamiento de resultados...")
            self._procesar_resultados_analisis(analisis_db, resultados, imagen_capturada)
            
            logger.info(f"✅ [DEBUG] Análisis completo finalizado: {id_analisis}")
            
            return {
                "id_analisis": id_analisis,
                "estado": "completado",
                "resultados": self._limpiar_resultados_para_json(resultados)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis completo: {e}")
            return {"error": str(e)}
    
    def realizar_analisis_clasificacion(self, usuario=None) -> Dict[str, Any]:
        """
        Realiza solo clasificación de cople usando la cámara real
        
        Args:
            usuario: Usuario que realiza el análisis
            
        Returns:
            Dict con el resultado del análisis
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            # Generar ID único para el análisis
            id_analisis = f"clasificacion_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            logger.info(f"🔄 Iniciando análisis de clasificación: {id_analisis}")
            
            # Capturar imagen de la cámara
            imagen_capturada = self._capturar_imagen()
            if imagen_capturada is None:
                return {"error": "No se pudo capturar imagen de la cámara"}
            
            logger.info(f"📸 Imagen capturada: {imagen_capturada.shape}")
            
            # Crear registro de análisis en la base de datos
            analisis_db = AnalisisCople.objects.create(
                id_analisis=id_analisis,
                timestamp_captura=timezone.now(),
                tipo_analisis='clasificacion',
                estado='procesando',
                configuracion=self.configuracion_activa,
                usuario=usuario,
                archivo_imagen=f"real_{id_analisis}.jpg",
                archivo_json=f"real_{id_analisis}.json",
                resolucion_ancho=imagen_capturada.shape[1],
                resolucion_alto=imagen_capturada.shape[0],
                resolucion_canales=imagen_capturada.shape[2] if len(imagen_capturada.shape) > 2 else 1,
                tiempo_captura_ms=50.0,
                tiempo_clasificacion_ms=0.0,
                tiempo_deteccion_piezas_ms=0.0,
                tiempo_deteccion_defectos_ms=0.0,
                tiempo_segmentacion_defectos_ms=0.0,
                tiempo_segmentacion_piezas_ms=0.0,
                tiempo_total_ms=0.0,
                metadatos_json={}
            )
            
            logger.info(f"📝 Registro de análisis creado en BD: {analisis_db.id}")
            
            # Realizar análisis de clasificación usando el sistema real
            resultados = self.sistema_analisis.solo_clasificacion()
            
            # Procesar resultados
            self._procesar_resultados_analisis(analisis_db, resultados, imagen_capturada)
            
            # Verificar que el análisis se guardó correctamente
            analisis_verificado = AnalisisCople.objects.filter(id_analisis=id_analisis).first()
            if analisis_verificado:
                logger.info(f"✅ Análisis verificado en BD: {analisis_verificado.id} - Estado: {analisis_verificado.estado}")
            else:
                logger.error(f"❌ Análisis NO encontrado en BD: {id_analisis}")
            
            logger.info(f"✅ Análisis de clasificación finalizado: {id_analisis}")
            
            return {
                "id_analisis": id_analisis,
                "estado": "completado",
                "resultados": self._limpiar_resultados_para_json(resultados)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de clasificación: {e}")
            return {"error": str(e)}

    def realizar_analisis_deteccion_piezas(self, usuario=None) -> Dict[str, Any]:
        """
        Realiza solo detección de piezas
        
        Args:
            usuario: Usuario que realiza el análisis
            
        Returns:
            Dict con los resultados del análisis
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            # Generar ID único para el análisis
            id_analisis = f"deteccion_piezas_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            logger.info(f"🔄 Iniciando análisis de detección de piezas: {id_analisis}")
            
            # Capturar imagen de la cámara
            imagen_capturada = self._capturar_imagen()
            if imagen_capturada is None:
                return {"error": "No se pudo capturar imagen de la cámara"}
            
            logger.info(f"📸 Imagen capturada: {imagen_capturada.shape}")
            
            # Crear registro de análisis en la base de datos
            analisis_db = AnalisisCople.objects.create(
                id_analisis=id_analisis,
                timestamp_captura=timezone.now(),
                tipo_analisis='deteccion_piezas',
                estado='procesando',
                configuracion=self.configuracion_activa,
                usuario=usuario,
                archivo_imagen=f"real_{id_analisis}.jpg",
                archivo_json=f"real_{id_analisis}.json",
                resolucion_ancho=imagen_capturada.shape[1],
                resolucion_alto=imagen_capturada.shape[0],
                resolucion_canales=imagen_capturada.shape[2] if len(imagen_capturada.shape) > 2 else 1,
                tiempo_captura_ms=50.0,
                tiempo_clasificacion_ms=0.0,
                tiempo_deteccion_piezas_ms=0.0,
                tiempo_deteccion_defectos_ms=0.0,
                tiempo_segmentacion_defectos_ms=0.0,
                tiempo_segmentacion_piezas_ms=0.0,
                tiempo_total_ms=0.0,
                metadatos_json={}
            )
            
            logger.info(f"📝 Registro de análisis creado en BD: {analisis_db.id}")
            
            # Realizar análisis de detección de piezas usando el sistema real
            resultados = self.sistema_analisis.solo_deteccion()
            
            # Procesar resultados
            self._procesar_resultados_analisis(analisis_db, resultados, imagen_capturada)
            
            logger.info(f"✅ Análisis de detección de piezas finalizado: {id_analisis}")
            
            return {
                "id_analisis": id_analisis,
                "estado": "completado",
                "resultados": self._limpiar_resultados_para_json(resultados)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de detección de piezas: {e}")
            return {"error": str(e)}

    def realizar_analisis_deteccion_defectos(self, usuario=None) -> Dict[str, Any]:
        """
        Realiza solo detección de defectos
        
        Args:
            usuario: Usuario que realiza el análisis
            
        Returns:
            Dict con los resultados del análisis
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            # Generar ID único para el análisis
            id_analisis = f"deteccion_defectos_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            logger.info(f"🔄 Iniciando análisis de detección de defectos: {id_analisis}")
            
            # Capturar imagen de la cámara
            imagen_capturada = self._capturar_imagen()
            if imagen_capturada is None:
                return {"error": "No se pudo capturar imagen de la cámara"}
            
            logger.info(f"📸 Imagen capturada: {imagen_capturada.shape}")
            
            # Crear registro de análisis en la base de datos
            analisis_db = AnalisisCople.objects.create(
                id_analisis=id_analisis,
                timestamp_captura=timezone.now(),
                tipo_analisis='deteccion_defectos',
                estado='procesando',
                configuracion=self.configuracion_activa,
                usuario=usuario,
                archivo_imagen=f"real_{id_analisis}.jpg",
                archivo_json=f"real_{id_analisis}.json",
                resolucion_ancho=imagen_capturada.shape[1],
                resolucion_alto=imagen_capturada.shape[0],
                resolucion_canales=imagen_capturada.shape[2] if len(imagen_capturada.shape) > 2 else 1,
                tiempo_captura_ms=50.0,
                tiempo_clasificacion_ms=0.0,
                tiempo_deteccion_piezas_ms=0.0,
                tiempo_deteccion_defectos_ms=0.0,
                tiempo_segmentacion_defectos_ms=0.0,
                tiempo_segmentacion_piezas_ms=0.0,
                tiempo_total_ms=0.0,
                metadatos_json={}
            )
            
            logger.info(f"📝 Registro de análisis creado en BD: {analisis_db.id}")
            
            # Realizar análisis de detección de defectos usando el sistema real
            resultados = self.sistema_analisis.solo_deteccion_defectos()
            
            # Procesar resultados
            self._procesar_resultados_analisis(analisis_db, resultados, imagen_capturada)
            
            logger.info(f"✅ Análisis de detección de defectos finalizado: {id_analisis}")
            
            return {
                "id_analisis": id_analisis,
                "estado": "completado",
                "resultados": self._limpiar_resultados_para_json(resultados)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de detección de defectos: {e}")
            return {"error": str(e)}

    def realizar_analisis_segmentacion_defectos(self, usuario=None) -> Dict[str, Any]:
        """
        Realiza solo segmentación de defectos
        
        Args:
            usuario: Usuario que realiza el análisis
            
        Returns:
            Dict con los resultados del análisis
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            # Generar ID único para el análisis
            id_analisis = f"segmentacion_defectos_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            logger.info(f"🔄 Iniciando análisis de segmentación de defectos: {id_analisis}")
            
            # Capturar imagen de la cámara
            imagen_capturada = self._capturar_imagen()
            if imagen_capturada is None:
                return {"error": "No se pudo capturar imagen de la cámara"}
            
            logger.info(f"📸 Imagen capturada: {imagen_capturada.shape}")
            
            # Crear registro de análisis en la base de datos
            analisis_db = AnalisisCople.objects.create(
                id_analisis=id_analisis,
                timestamp_captura=timezone.now(),
                tipo_analisis='segmentacion_defectos',
                estado='procesando',
                configuracion=self.configuracion_activa,
                usuario=usuario,
                archivo_imagen=f"real_{id_analisis}.jpg",
                archivo_json=f"real_{id_analisis}.json",
                resolucion_ancho=imagen_capturada.shape[1],
                resolucion_alto=imagen_capturada.shape[0],
                resolucion_canales=imagen_capturada.shape[2] if len(imagen_capturada.shape) > 2 else 1,
                tiempo_captura_ms=50.0,
                tiempo_clasificacion_ms=0.0,
                tiempo_deteccion_piezas_ms=0.0,
                tiempo_deteccion_defectos_ms=0.0,
                tiempo_segmentacion_defectos_ms=0.0,
                tiempo_segmentacion_piezas_ms=0.0,
                tiempo_total_ms=0.0,
                metadatos_json={}
            )
            
            logger.info(f"📝 Registro de análisis creado en BD: {analisis_db.id}")
            
            # Realizar análisis de segmentación de defectos usando el sistema real
            resultados = self.sistema_analisis.solo_segmentacion_defectos()
            
            # Procesar resultados
            self._procesar_resultados_analisis(analisis_db, resultados, imagen_capturada)
            
            logger.info(f"✅ Análisis de segmentación de defectos finalizado: {id_analisis}")
            
            return {
                "id_analisis": id_analisis,
                "estado": "completado",
                "resultados": self._limpiar_resultados_para_json(resultados)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de segmentación de defectos: {e}")
            return {"error": str(e)}

    def realizar_analisis_segmentacion_piezas(self, usuario=None) -> Dict[str, Any]:
        """
        Realiza solo segmentación de piezas
        
        Args:
            usuario: Usuario que realiza el análisis
            
        Returns:
            Dict con los resultados del análisis
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            # Generar ID único para el análisis
            id_analisis = f"segmentacion_piezas_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            logger.info(f"🔄 Iniciando análisis de segmentación de piezas: {id_analisis}")
            
            # Capturar imagen de la cámara
            imagen_capturada = self._capturar_imagen()
            if imagen_capturada is None:
                return {"error": "No se pudo capturar imagen de la cámara"}
            
            logger.info(f"📸 Imagen capturada: {imagen_capturada.shape}")
            
            # Crear registro de análisis en la base de datos
            analisis_db = AnalisisCople.objects.create(
                id_analisis=id_analisis,
                timestamp_captura=timezone.now(),
                tipo_analisis='segmentacion_piezas',
                estado='procesando',
                configuracion=self.configuracion_activa,
                usuario=usuario,
                archivo_imagen=f"real_{id_analisis}.jpg",
                archivo_json=f"real_{id_analisis}.json",
                resolucion_ancho=imagen_capturada.shape[1],
                resolucion_alto=imagen_capturada.shape[0],
                resolucion_canales=imagen_capturada.shape[2] if len(imagen_capturada.shape) > 2 else 1,
                tiempo_captura_ms=50.0,
                tiempo_clasificacion_ms=0.0,
                tiempo_deteccion_piezas_ms=0.0,
                tiempo_deteccion_defectos_ms=0.0,
                tiempo_segmentacion_defectos_ms=0.0,
                tiempo_segmentacion_piezas_ms=0.0,
                tiempo_total_ms=0.0,
                metadatos_json={}
            )
            
            logger.info(f"📝 Registro de análisis creado en BD: {analisis_db.id}")
            
            # Realizar análisis de segmentación de piezas usando el sistema real
            resultados = self.sistema_analisis.solo_segmentacion_piezas()
            
            # Procesar resultados
            self._procesar_resultados_analisis(analisis_db, resultados, imagen_capturada)
            
            logger.info(f"✅ Análisis de segmentación de piezas finalizado: {id_analisis}")
            
            return {
                "id_analisis": id_analisis,
                "estado": "completado",
                "resultados": self._limpiar_resultados_para_json(resultados)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de segmentación de piezas: {e}")
            return {"error": str(e)}
    
    def _capturar_imagen(self) -> Optional[np.ndarray]:
        """Captura una imagen usando el sistema integrado"""
        try:
            if not self.sistema_analisis or not self.inicializado:
                logger.error("Sistema de análisis no inicializado")
                return None
            
            # Usar el sistema integrado para capturar imagen
            resultado = self.sistema_analisis.capturar_imagen_unica()
            if resultado is None or "error" in resultado:
                logger.error(f"No se pudo capturar frame del sistema integrado: {resultado.get('error', 'Error desconocido')}")
                return None
            
            # Extraer el frame del diccionario de resultados
            frame = resultado.get("frame")
            if frame is None:
                logger.error("Frame no encontrado en resultado de captura")
                return None
            
            logger.info(f"📸 Imagen capturada: {frame.shape}")
            return frame
                
        except Exception as e:
            logger.error(f"Error capturando imagen: {e}")
            return None
    
    def _procesar_frame(self, frame: np.ndarray) -> np.ndarray:
        """Procesa el frame para obtener imagen de 640x640"""
        try:
            height, width = frame.shape[:2]
            
            # Si la imagen ya es 640x640, devolverla tal como está
            if width == 640 and height == 640:
                return frame
            
            # Calcular recorte centrado
            if width >= 640 and height >= 640:
                # Recorte centrado
                start_x = (width - 640) // 2
                start_y = (height - 640) // 2
                return frame[start_y:start_y+640, start_x:start_x+640]
            else:
                # Redimensionar si es menor
                return cv2.resize(frame, (640, 640))
                
        except Exception as e:
            logger.error(f"Error procesando frame: {e}")
            return frame
    
    def _analizar_imagen_webcam(self, imagen: np.ndarray) -> Dict[str, Any]:
        """Analiza una imagen capturada de webcam (versión simplificada)"""
        import random
        
        # Simular análisis basado en características de la imagen
        # En una implementación real, aquí se usarían los modelos de IA
        
        # Análisis básico de la imagen
        altura, ancho = imagen.shape[:2]
        brillo_promedio = np.mean(imagen)
        
        # Simular clasificación basada en características
        if brillo_promedio > 120:
            clase = 'Aceptado'
            confianza = random.uniform(0.8, 0.95)
        else:
            clase = 'Rechazado'
            confianza = random.uniform(0.7, 0.9)
        
        # Simular detecciones
        detecciones_piezas = []
        detecciones_defectos = []
        
        # Generar detecciones basadas en el tamaño de la imagen
        for i in range(random.randint(1, 3)):
            x1 = random.randint(50, ancho - 200)
            y1 = random.randint(50, altura - 200)
            x2 = x1 + random.randint(80, 150)
            y2 = y1 + random.randint(80, 150)
            
            detecciones_piezas.append({
                "clase": f"Pieza_{i+1}",
                "confianza": random.uniform(0.8, 0.95),
                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                "centroide": {"x": (x1 + x2) // 2, "y": (y1 + y2) // 2},
                "area": (x2 - x1) * (y2 - y1)
            })
        
        return {
            "clasificacion": {
                "clase": clase,
                "confianza": confianza,
                "tiempo_inferencia_ms": 120.0
            },
            "detecciones_piezas": detecciones_piezas,
            "detecciones_defectos": detecciones_defectos,
            "tiempos": {
                "captura_ms": 50.0,
                "clasificacion_ms": 120.0,
                "deteccion_piezas_ms": 200.0,
                "deteccion_defectos_ms": 180.0,
                "segmentacion_defectos_ms": 300.0,
                "segmentacion_piezas_ms": 280.0,
                "total_ms": 1130.0
            },
            "sistema": {
                "version": "1.0.0-webcam",
                "configuracion": self.configuracion_activa.nombre if self.configuracion_activa else "default",
                "camera_type": "webcam"
            }
        }
    
    def _analizar_clasificacion_webcam(self, imagen: np.ndarray) -> Dict[str, Any]:
        """Analiza solo clasificación de una imagen de webcam"""
        import random
        
        # Análisis básico de la imagen
        brillo_promedio = np.mean(imagen)
        
        # Simular clasificación basada en características
        if brillo_promedio > 120:
            clase = 'Aceptado'
            confianza = random.uniform(0.8, 0.95)
        else:
            clase = 'Rechazado'
            confianza = random.uniform(0.7, 0.9)
        
        return {
            "clasificacion": {
                "clase": clase,
                "confianza": confianza,
                "tiempo_inferencia_ms": 120.0
            },
            "tiempos": {
                "captura_ms": 50.0,
                "clasificacion_ms": 120.0,
                "total_ms": 170.0
            },
            "sistema": {
                "version": "1.0.0-webcam",
                "configuracion": self.configuracion_activa.nombre if self.configuracion_activa else "default",
                "camera_type": "webcam"
            }
        }
    
    def _procesar_resultados_analisis(self, analisis_db: AnalisisCople, resultados: Dict[str, Any], imagen: np.ndarray = None):
        """
        Procesa los resultados del análisis y los guarda en la base de datos
        
        Args:
            analisis_db: Instancia del modelo AnalisisCople
            resultados: Resultados del análisis
            imagen: Imagen capturada (opcional, puede venir en resultados)
        """
        try:
            logger.info(f"💾 [DEBUG] _procesar_resultados_analisis iniciado")
            logger.info(f"   📊 Tipo de resultados: {type(resultados)}")
            logger.info(f"   📋 Claves en resultados: {list(resultados.keys()) if isinstance(resultados, dict) else 'No es dict'}")
            logger.info(f"   🖼️ Imagen proporcionada: {imagen is not None}")
            if imagen is not None:
                logger.info(f"   🖼️ Imagen shape: {imagen.shape}, dtype: {imagen.dtype}")
            
            # Obtener imagen de los resultados si no se proporciona
            if imagen is None and "frame" in resultados:
                logger.info(f"   🖼️ [DEBUG] Obteniendo imagen de resultados['frame']")
                imagen = resultados["frame"]
                logger.info(f"   🖼️ [DEBUG] Imagen obtenida: {imagen.shape if imagen is not None else 'None'}")
            
            # Actualizar tiempos
            if "tiempos" in resultados:
                tiempos = resultados["tiempos"]
                analisis_db.tiempo_captura_ms = tiempos.get('captura_ms', 0.0)
                analisis_db.tiempo_clasificacion_ms = tiempos.get('clasificacion_ms', 0.0)
                analisis_db.tiempo_deteccion_piezas_ms = tiempos.get('deteccion_piezas_ms', 0.0)
                analisis_db.tiempo_deteccion_defectos_ms = tiempos.get('deteccion_defectos_ms', 0.0)
                analisis_db.tiempo_segmentacion_defectos_ms = tiempos.get('segmentacion_defectos_ms', 0.0)
                analisis_db.tiempo_segmentacion_piezas_ms = tiempos.get('segmentacion_piezas_ms', 0.0)
                analisis_db.tiempo_total_ms = tiempos.get('total_ms', 0.0)
            
            # Guardar metadatos JSON completos (convirtiendo frame a base64)
            resultados_json = resultados.copy()
            if "frame" in resultados_json:
                # Convertir frame de numpy a base64 para serialización
                import cv2
                import base64
                frame = resultados_json["frame"]
                if isinstance(frame, np.ndarray):
                    # Asegurar que el frame esté en formato uint8 (como en Expo_modelos)
                    if frame.dtype != np.uint8:
                        if frame.dtype == np.float32 or frame.dtype == np.float64:
                            # Asumir que está en rango [0, 1] y convertir a [0, 255]
                            frame = (frame * 255).astype(np.uint8)
                        else:
                            frame = frame.astype(np.uint8)
                    
                    # NO convertir de BGR a RGB aquí - cv2.imencode espera BGR
                    # El frame ya viene en BGR desde OpenCV, mantenerlo así
                    frame_bgr = frame
                    
                    # Codificar a base64 usando JPG (como en Expo_modelos)
                    _, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    resultados_json["frame"] = frame_base64
                    logger.info(f"✅ Frame guardado como base64 JPG: {len(frame_base64)} caracteres, shape: {frame_bgr.shape}, dtype: {frame_bgr.dtype}")
                else:
                    del resultados_json["frame"]  # Remover si no es numpy array
            
            # Limpiar resultados_json para que sea serializable a JSON
            logger.info(f"🧹 [DEBUG] Limpiando resultados para JSON...")
            resultados_json_limpios = self._limpiar_resultados_para_json(resultados_json)
            logger.info(f"🧹 [DEBUG] Resultados limpiados. Asignando a metadatos_json...")
            
            # Verificar que no hay arrays de NumPy antes de asignar
            import json
            try:
                json.dumps(resultados_json_limpios)
                logger.info(f"✅ [DEBUG] Resultados son serializables a JSON")
            except TypeError as e:
                logger.error(f"❌ [DEBUG] Resultados NO son serializables: {e}")
                # Limpiar más profundamente
                resultados_json_limpios = self._limpiar_resultados_para_json_recursivo(resultados_json_limpios)
                logger.info(f"🧹 [DEBUG] Limpieza recursiva aplicada")
                
                # Verificar nuevamente después de la limpieza recursiva
                try:
                    json.dumps(resultados_json_limpios)
                    logger.info(f"✅ [DEBUG] Resultados son serializables después de limpieza recursiva")
                except TypeError as e2:
                    logger.error(f"❌ [DEBUG] Resultados AÚN NO son serializables después de limpieza recursiva: {e2}")
                    # Como último recurso, crear un diccionario simplificado
                    resultados_json_limpios = {
                        "error": "Error de serialización",
                        "timestamp": str(timezone.now()),
                        "tipo_analisis": "segmentacion_defectos"
                    }
            
            analisis_db.metadatos_json = resultados_json_limpios
            
            # Procesar resultados específicos
            self._guardar_resultados_clasificacion(analisis_db, resultados)
            self._guardar_detecciones_piezas(analisis_db, resultados)
            self._guardar_detecciones_defectos(analisis_db, resultados)
            self._guardar_segmentaciones_defectos(analisis_db, resultados)
            self._guardar_segmentaciones_piezas(analisis_db, resultados)
            
            # Guardar imagen procesada si está disponible
            if imagen is not None:
                self._guardar_imagen_procesada(analisis_db, imagen, resultados)
            
            # Marcar como completado
            analisis_db.estado = 'completado'
            analisis_db.save()
            
        except Exception as e:
            logger.error(f"Error procesando resultados: {e}")
            analisis_db.estado = 'error'
            analisis_db.mensaje_error = str(e)
            analisis_db.save()
    
    def _guardar_imagen_procesada(self, analisis_db: AnalisisCople, imagen: np.ndarray, resultados: Dict[str, Any]):
        """Guarda la imagen procesada con los resultados superpuestos"""
        try:
            logger.info(f"🖼️ [DEBUG] _guardar_imagen_procesada iniciado")
            logger.info(f"   🖼️ Imagen shape: {imagen.shape}, dtype: {imagen.dtype}")
            logger.info(f"   📊 Resultados tipo: {type(resultados)}")
            logger.info(f"   📋 Claves en resultados: {list(resultados.keys()) if isinstance(resultados, dict) else 'No es dict'}")
            
            # Crear imagen procesada con resultados
            logger.info(f"🎨 [DEBUG] Creando imagen procesada...")
            imagen_procesada = self._crear_imagen_procesada(imagen, resultados)
            logger.info(f"🎨 [DEBUG] Imagen procesada creada: {imagen_procesada.shape}, dtype: {imagen_procesada.dtype}")
            
            # Convertir a bytes
            _, buffer = cv2.imencode('.jpg', imagen_procesada)
            imagen_bytes = buffer.tobytes()
            
            # Guardar en storage
            nombre_archivo = f"procesada_{analisis_db.id_analisis}.jpg"
            archivo = ContentFile(imagen_bytes, name=nombre_archivo)
            
            # Guardar archivo
            logger.info(f"💾 [DEBUG] Guardando archivo en storage...")
            ruta_archivo = default_storage.save(f"analisis/{nombre_archivo}", archivo)
            logger.info(f"💾 [DEBUG] Archivo guardado en: {ruta_archivo}")
            
            logger.info(f"💾 [DEBUG] Asignando ruta al modelo...")
            analisis_db.archivo_imagen = ruta_archivo
            analisis_db.imagen_procesada = archivo  # Guardar también en el campo imagen_procesada
            
            logger.info(f"💾 [DEBUG] Guardando modelo en base de datos...")
            analisis_db.save()
            
            logger.info(f"✅ [DEBUG] Imagen procesada guardada exitosamente: {ruta_archivo}")
            
        except Exception as e:
            logger.error(f"Error guardando imagen procesada: {e}")
    
    def _crear_imagen_procesada(self, imagen: np.ndarray, resultados: Dict[str, Any]) -> np.ndarray:
        """Crea una imagen procesada con los resultados superpuestos"""
        try:
            logger.info(f"🎨 [DEBUG] _crear_imagen_procesada iniciado")
            logger.info(f"   🖼️ Imagen entrada: {imagen.shape}, dtype: {imagen.dtype}")
            logger.info(f"   📊 Resultados tipo: {type(resultados)}")
            logger.info(f"   📋 Claves disponibles: {list(resultados.keys()) if isinstance(resultados, dict) else 'No es dict'}")
            
            # CORRECCIÓN: Si hay segmentaciones de defectos, usar el mismo flujo que Expo_modelos
            if "segmentaciones_defectos" in resultados and len(resultados["segmentaciones_defectos"]) > 0:
                logger.info(f"🎭 [DEBUG] Detectadas segmentaciones de defectos, usando flujo de Expo_modelos")
                logger.info(f"   📊 Cantidad de segmentaciones: {len(resultados['segmentaciones_defectos'])}")
                
                # Importar el procesador de segmentación de defectos
                try:
                    from .modules.segmentation.defectos_segmentation_processor import ProcesadorSegmentacionDefectos
                    logger.info(f"✅ [DEBUG] Import exitoso de ProcesadorSegmentacionDefectos")
                except Exception as e:
                    logger.error(f"❌ [DEBUG] Error importando ProcesadorSegmentacionDefectos: {e}")
                    raise
                
                # Crear instancia del procesador
                try:
                    procesador = ProcesadorSegmentacionDefectos()
                    logger.info(f"✅ [DEBUG] Instancia de procesador creada exitosamente")
                except Exception as e:
                    logger.error(f"❌ [DEBUG] Error creando instancia del procesador: {e}")
                    raise
                
                # Verificar que mask_visualizer existe
                if hasattr(procesador, 'mask_visualizer'):
                    logger.info(f"✅ [DEBUG] mask_visualizer encontrado en procesador")
                    if hasattr(procesador.mask_visualizer, 'visualizar_mascaras_completo'):
                        logger.info(f"✅ [DEBUG] método visualizar_mascaras_completo encontrado")
                    else:
                        logger.error(f"❌ [DEBUG] método visualizar_mascaras_completo NO encontrado")
                        logger.info(f"   📋 Métodos disponibles: {[m for m in dir(procesador.mask_visualizer) if not m.startswith('_')]}")
                else:
                    logger.error(f"❌ [DEBUG] mask_visualizer NO encontrado en procesador")
                    logger.info(f"   📋 Atributos disponibles: {[a for a in dir(procesador) if not a.startswith('_')]}")
                
                # Usar el mismo método que Expo_modelos para generar la imagen con máscaras
                try:
                    logger.info(f"🎨 [DEBUG] Llamando a visualizar_mascaras_completo...")
                    logger.info(f"   🖼️ Imagen entrada: {imagen.shape}, dtype: {imagen.dtype}")
                    logger.info(f"   📊 Segmentaciones: {len(resultados['segmentaciones_defectos'])}")
                    
                    imagen_procesada = procesador.mask_visualizer.visualizar_mascaras_completo(
                        imagen, 
                        resultados["segmentaciones_defectos"], 
                        mostrar=False
                    )
                    
                    logger.info(f"✅ [DEBUG] Imagen con máscaras generada exitosamente")
                    logger.info(f"   🖼️ Imagen salida: {imagen_procesada.shape}, dtype: {imagen_procesada.dtype}")
                    logger.info(f"   🎨 Valores únicos en imagen: {len(np.unique(imagen_procesada))}")
                    logger.info(f"   🎨 Rango de valores: [{imagen_procesada.min()}, {imagen_procesada.max()}]")
                    
                except Exception as e:
                    logger.error(f"❌ [DEBUG] Error generando imagen con máscaras: {e}")
                    logger.error(f"   📋 Tipo de error: {type(e).__name__}")
                    import traceback
                    logger.error(f"   📋 Traceback: {traceback.format_exc()}")
                    # Fallback a imagen original
                    imagen_procesada = imagen.copy()
                    logger.info(f"   🖼️ Usando imagen original como fallback: {imagen_procesada.shape}, dtype: {imagen_procesada.dtype}")
            else:
                # Copiar imagen original solo si no hay segmentaciones
                imagen_procesada = imagen.copy()
                logger.info(f"   🖼️ Imagen copiada: {imagen_procesada.shape}, dtype: {imagen_procesada.dtype}")
            
            # Dibujar detecciones de piezas
            if "detecciones_piezas" in resultados:
                for deteccion in resultados["detecciones_piezas"]:
                    bbox = deteccion.get("bbox", {})
                    x1, y1 = bbox.get("x1", 0), bbox.get("y1", 0)
                    x2, y2 = bbox.get("x2", 0), bbox.get("y2", 0)
                    
                    # Dibujar rectángulo verde para piezas
                    cv2.rectangle(imagen_procesada, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Dibujar etiqueta
                    etiqueta = f"{deteccion.get('clase', 'Pieza')} ({deteccion.get('confianza', 0):.2f})"
                    cv2.putText(imagen_procesada, etiqueta, (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Dibujar detecciones de defectos
            if "detecciones_defectos" in resultados:
                for deteccion in resultados["detecciones_defectos"]:
                    bbox = deteccion.get("bbox", {})
                    x1, y1 = bbox.get("x1", 0), bbox.get("y1", 0)
                    x2, y2 = bbox.get("x2", 0), bbox.get("y2", 0)
                    
                    # Dibujar rectángulo rojo para defectos
                    cv2.rectangle(imagen_procesada, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    
                    # Dibujar etiqueta
                    etiqueta = f"{deteccion.get('clase', 'Defecto')} ({deteccion.get('confianza', 0):.2f})"
                    cv2.putText(imagen_procesada, etiqueta, (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # CORRECCIÓN: Para segmentaciones de defectos, las máscaras ya están renderizadas por MaskVisualizer
            # Solo agregamos información adicional si es necesario
            if "segmentaciones_defectos" in resultados:
                logger.info(f"🎯 [DEBUG] Segmentaciones de defectos detectadas - máscaras ya renderizadas por MaskVisualizer")
                segmentaciones_defectos = resultados["segmentaciones_defectos"]
                logger.info(f"   📊 Cantidad: {len(segmentaciones_defectos) if isinstance(segmentaciones_defectos, list) else 'No es lista'}")
                
                # Las máscaras ya están renderizadas, solo agregamos información de debug
                for i, segmentacion in enumerate(segmentaciones_defectos):
                    if isinstance(segmentacion, dict) and "mascara" in segmentacion:
                        mascara = segmentacion["mascara"]
                        logger.info(f"   🎭 Segmentación {i}: Máscara {mascara.shape if hasattr(mascara, 'shape') else 'N/A'}")
                        if mascara is not None and hasattr(mascara, 'min'):
                            logger.info(f"      🎭 Máscara min/max: {mascara.min()}/{mascara.max()}")
                
                logger.info(f"✅ [DEBUG] Máscaras de segmentación ya renderizadas por MaskVisualizer - no sobrescribiendo")
            
            # CORRECCIÓN: Si hay segmentaciones de piezas, usar el flujo de Expo_modelos
            if "segmentaciones_piezas" in resultados and len(resultados["segmentaciones_piezas"]) > 0:
                logger.info(f"🎭 [DEBUG] Detectadas segmentaciones de piezas. Usando flujo de Expo_modelos para renderizado.")
                
                # Importar el procesador de segmentación de piezas
                from .modules.segmentation.piezas_segmentation_processor import ProcesadorSegmentacionPiezas
                
                # Crear instancia del procesador
                procesador = ProcesadorSegmentacionPiezas()
                
                # Usar el mismo método que Expo_modelos para generar la imagen con máscaras
                try:
                    # El procesador de piezas usa _crear_visualizacion que ya incluye máscaras
                    imagen_procesada = procesador._crear_visualizacion(imagen, resultados["segmentaciones_piezas"])
                    logger.info(f"🎭 [DEBUG] Imagen procesada con máscaras de piezas de Expo_modelos: {imagen_procesada.shape}, dtype: {imagen_procesada.dtype}")
                except Exception as e:
                    logger.error(f"❌ Error en procesador de piezas: {e}")
                    # Fallback: dibujar solo bounding boxes
                    for i, segmentacion in enumerate(resultados["segmentaciones_piezas"]):
                        bbox = segmentacion.get("bbox", {})
                        x1, y1 = bbox.get("x1", 0), bbox.get("y1", 0)
                        x2, y2 = bbox.get("x2", 0), bbox.get("y2", 0)
                        
                        # Dibujar rectángulo verde para piezas
                        cv2.rectangle(imagen_procesada, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Dibujar etiqueta
                        etiqueta = f"Pieza ({segmentacion.get('confianza', 0):.2f})"
                        cv2.putText(imagen_procesada, etiqueta, (x1, y1-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Dibujar resultado de clasificación
            if "clasificacion" in resultados:
                clasificacion = resultados["clasificacion"]
                clase = clasificacion.get("clase", "Desconocido")
                confianza = clasificacion.get("confianza", 0.0)
                
                # Color según resultado
                color = (0, 255, 0) if clase == "Aceptado" else (0, 0, 255)
                
                # Dibujar texto de clasificación
                texto = f"{clase} ({confianza:.2f})"
                cv2.putText(imagen_procesada, texto, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            return imagen_procesada
            
        except Exception as e:
            logger.error(f"Error creando imagen procesada: {e}")
            return imagen
    
    def _dibujar_mascara(self, imagen: np.ndarray, mascara: np.ndarray, color: tuple):
        """
        Dibuja una máscara sobre la imagen con transparencia
        
        Args:
            imagen: Imagen base (BGR)
            mascara: Máscara binaria (0-1 o 0-255)
            color: Color en formato (B, G, R, alpha)
        """
        try:
            # Reducir logging para evitar problemas de memoria
            logger.debug(f"🎭 Dibujando máscara: {mascara.shape if hasattr(mascara, 'shape') else 'N/A'}")
            
            # Verificar que la máscara sea un array de NumPy válido
            if not isinstance(mascara, np.ndarray):
                logger.warning(f"❌ [DEBUG] Máscara no es un array de NumPy: {type(mascara)}")
                return
            
            # Verificar que la máscara no esté vacía
            if mascara.size == 0:
                logger.warning("Máscara está vacía")
                return
            
            # Convertir máscara a uint8 si es necesario
            if mascara.dtype != np.uint8:
                if mascara.max() <= 1.0:
                    mascara = (mascara * 255).astype(np.uint8)
                else:
                    mascara = mascara.astype(np.uint8)
            
            # Redimensionar máscara si es necesario
            if mascara.shape != imagen.shape[:2]:
                mascara = cv2.resize(mascara, (imagen.shape[1], imagen.shape[0]))
            
            # Crear overlay con color
            overlay = imagen.copy()
            overlay[mascara > 0] = color[:3]  # BGR
            
            # Aplicar transparencia
            alpha = color[3] / 255.0 if len(color) > 3 else 0.3
            cv2.addWeighted(overlay, alpha, imagen, 1 - alpha, 0, imagen)
            
        except Exception as e:
            logger.error(f"Error dibujando máscara: {e}")
            # No re-lanzar la excepción para evitar que se propague
    
    def _guardar_resultados_clasificacion(self, analisis_db: AnalisisCople, resultados: Dict[str, Any]):
        """Guarda los resultados de clasificación"""
        if "clasificacion" not in resultados:
            return
        
        clasificacion = resultados["clasificacion"]
        
        ResultadoClasificacion.objects.create(
            analisis=analisis_db,
            clase_predicha=clasificacion.get("clase", ""),
            confianza=clasificacion.get("confianza", 0.0),
            tiempo_inferencia_ms=clasificacion.get("tiempo_inferencia_ms", 0.0)
        )
    
    def _guardar_detecciones_piezas(self, analisis_db: AnalisisCople, resultados: Dict[str, Any]):
        """Guarda las detecciones de piezas"""
        if "detecciones_piezas" not in resultados:
            return
        
        for deteccion in resultados["detecciones_piezas"]:
            bbox = deteccion.get("bbox", {})
            centroide = deteccion.get("centroide", {})
            
            DeteccionPieza.objects.create(
                analisis=analisis_db,
                clase=deteccion.get("clase", ""),
                confianza=deteccion.get("confianza", 0.0),
                bbox_x1=bbox.get("x1", 0),
                bbox_y1=bbox.get("y1", 0),
                bbox_x2=bbox.get("x2", 0),
                bbox_y2=bbox.get("y2", 0),
                centroide_x=centroide.get("x", 0),
                centroide_y=centroide.get("y", 0),
                area=deteccion.get("area", 0)
            )
    
    def _guardar_detecciones_defectos(self, analisis_db: AnalisisCople, resultados: Dict[str, Any]):
        """Guarda las detecciones de defectos"""
        if "detecciones_defectos" not in resultados:
            return
        
        for deteccion in resultados["detecciones_defectos"]:
            bbox = deteccion.get("bbox", {})
            centroide = deteccion.get("centroide", {})
            
            DeteccionDefecto.objects.create(
                analisis=analisis_db,
                clase=deteccion.get("clase", ""),
                confianza=deteccion.get("confianza", 0.0),
                bbox_x1=bbox.get("x1", 0),
                bbox_y1=bbox.get("y1", 0),
                bbox_x2=bbox.get("x2", 0),
                bbox_y2=bbox.get("y2", 0),
                centroide_x=centroide.get("x", 0),
                centroide_y=centroide.get("y", 0),
                area=deteccion.get("area", 0)
            )
    
    def _guardar_segmentaciones_defectos(self, analisis_db: AnalisisCople, resultados: Dict[str, Any]):
        """Guarda las segmentaciones de defectos"""
        if "segmentaciones_defectos" not in resultados:
            return
        
        for segmentacion in resultados["segmentaciones_defectos"]:
            bbox = segmentacion.get("bbox", {})
            centroide = segmentacion.get("centroide", {})
            
            # Convertir máscara a base64 si está disponible
            mascara_base64 = None
            try:
                if "mascara" in segmentacion and segmentacion["mascara"] is not None:
                    mascara = segmentacion["mascara"]
                    if isinstance(mascara, np.ndarray):
                        # Convertir máscara a uint8 si es necesario
                        if mascara.dtype != np.uint8:
                            mascara = (mascara * 255).astype(np.uint8)
                        
                        # Codificar como PNG para preservar la máscara
                        _, buffer = cv2.imencode('.png', mascara)
                        mascara_base64 = base64.b64encode(buffer).decode('utf-8')
            except Exception as e:
                print(f"⚠️ Error procesando máscara para segmentación de defectos: {e}")
                mascara_base64 = None
            
            # Convertir coeficientes_mascara a lista si es un array de NumPy
            coeficientes_mascara = segmentacion.get("coeficientes_mascara", [])
            if isinstance(coeficientes_mascara, np.ndarray):
                coeficientes_mascara = coeficientes_mascara.tolist()
            
            SegmentacionDefecto.objects.create(
                analisis=analisis_db,
                clase=segmentacion.get("clase", ""),
                confianza=segmentacion.get("confianza", 0.0),
                bbox_x1=bbox.get("x1", 0),
                bbox_y1=bbox.get("y1", 0),
                bbox_x2=bbox.get("x2", 0),
                bbox_y2=bbox.get("y2", 0),
                centroide_x=centroide.get("x", 0),
                centroide_y=centroide.get("y", 0),
                area_mascara=segmentacion.get("area_mascara", segmentacion.get("area", 0)),
                coeficientes_mascara=coeficientes_mascara
            )
    
    def _guardar_segmentaciones_piezas(self, analisis_db: AnalisisCople, resultados: Dict[str, Any]):
        """Guarda las segmentaciones de piezas"""
        if "segmentaciones_piezas" not in resultados:
            return
        
        for segmentacion in resultados["segmentaciones_piezas"]:
            bbox = segmentacion.get("bbox", {})
            centroide = segmentacion.get("centroide", {})
            
            # Convertir máscara a base64 si está disponible
            mascara_base64 = None
            try:
                if "mascara" in segmentacion and segmentacion["mascara"] is not None:
                    mascara = segmentacion["mascara"]
                    if isinstance(mascara, np.ndarray):
                        # Convertir máscara a uint8 si es necesario
                        if mascara.dtype != np.uint8:
                            mascara = (mascara * 255).astype(np.uint8)
                        
                        # Codificar como PNG para preservar la máscara
                        _, buffer = cv2.imencode('.png', mascara)
                        mascara_base64 = base64.b64encode(buffer).decode('utf-8')
            except Exception as e:
                print(f"⚠️ Error procesando máscara para segmentación de piezas: {e}")
                mascara_base64 = None
            
            # Convertir coeficientes_mascara a lista si es un array de NumPy
            coeficientes_mascara = segmentacion.get("coeficientes_mascara", [])
            if isinstance(coeficientes_mascara, np.ndarray):
                coeficientes_mascara = coeficientes_mascara.tolist()
            
            SegmentacionPieza.objects.create(
                analisis=analisis_db,
                clase=segmentacion.get("clase", ""),
                confianza=segmentacion.get("confianza", 0.0),
                bbox_x1=bbox.get("x1", 0),
                bbox_y1=bbox.get("y1", 0),
                bbox_x2=bbox.get("x2", 0),
                bbox_y2=bbox.get("y2", 0),
                centroide_x=centroide.get("x", 0),
                centroide_y=centroide.get("y", 0),
                area_mascara=segmentacion.get("area_mascara", segmentacion.get("area", 0)),
                ancho_mascara=segmentacion.get("ancho_mascara", 0),
                alto_mascara=segmentacion.get("alto_mascara", 0),
                coeficientes_mascara=coeficientes_mascara
            )
    
    def obtener_estadisticas_sistema(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del sistema de análisis
        
        Returns:
            Dict con estadísticas del sistema
        """
        try:
            if not self.inicializado:
                return {"error": "Sistema no inicializado"}
            
            # Obtener estadísticas de la base de datos
            total_analisis = AnalisisCople.objects.count()
            analisis_exitosos = AnalisisCople.objects.filter(estado='completado').count()
            analisis_con_error = AnalisisCople.objects.filter(estado='error').count()
            
            # Obtener estadísticas del sistema real (simplificado)
            estadisticas_camara = {
                "inicializado": self.inicializado,
                "usando_webcam": self.usando_webcam,
                "configuracion_activa": self.configuracion_activa.nombre if self.configuracion_activa else "N/A"
            }
            
            return {
                "sistema_integrado": {
                    "version": "1.0.0-real",
                    "estado": "funcionando",
                    "modo": "real",
                    "camera_type": "webcam"
                },
                "base_datos": {
                    "total_analisis": total_analisis,
                    "analisis_exitosos": analisis_exitosos,
                    "analisis_con_error": analisis_con_error,
                    "tasa_exito": (analisis_exitosos / total_analisis * 100) if total_analisis > 0 else 0
                },
                "configuracion_activa": {
                    "nombre": self.configuracion_activa.nombre if self.configuracion_activa else None,
                    "umbral_confianza": self.configuracion_activa.umbral_confianza if self.configuracion_activa else None,
                    "configuracion_robustez": self.configuracion_activa.configuracion_robustez if self.configuracion_activa else None
                },
                "estadisticas_camara": estadisticas_camara
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
    
    def _limpiar_resultados_para_json(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Limpia los resultados para que sean serializables a JSON
        Maneja las máscaras de manera especial para evitar conversión a listas enormes
        """
        try:
            resultados_limpios = {}
            
            for clave, valor in resultados.items():
                if isinstance(valor, np.ndarray):
                    # Para máscaras, mantener como información de metadatos en lugar de convertir a lista
                    if clave == "mascara" or "mascara" in clave.lower():
                        # Crear información de metadatos de la máscara (como en Expo_modelos)
                        resultados_limpios[clave] = {
                            "shape": list(valor.shape),
                            "dtype": str(valor.dtype),
                            "min": float(valor.min()),
                            "max": float(valor.max()),
                            "pixels_activos": int(np.sum(valor > 0.5)),
                            "total_pixels": int(valor.size),
                            "tiene_contenido": bool(np.any(valor > 0.5))
                        }
                    else:
                        # Para otros arrays, convertir a lista solo si son pequeños
                        if valor.size < 1000:  # Solo arrays pequeños
                            resultados_limpios[clave] = valor.tolist()
                        else:
                            # Para arrays grandes, crear información de metadatos
                            resultados_limpios[clave] = {
                                "shape": list(valor.shape),
                                "dtype": str(valor.dtype),
                                "min": float(valor.min()),
                                "max": float(valor.max()),
                                "size": int(valor.size)
                            }
                elif isinstance(valor, dict):
                    resultados_limpios[clave] = self._limpiar_resultados_para_json(valor)
                elif isinstance(valor, list):
                    resultados_limpios[clave] = self._limpiar_lista_para_json(valor)
                else:
                    resultados_limpios[clave] = valor
            
            return resultados_limpios
            
        except Exception as e:
            logger.error(f"Error limpiando resultados para JSON: {e}")
            return {"error": "Error procesando resultados"}
    
    def _limpiar_lista_para_json(self, lista: list) -> list:
        """
        Limpia una lista para JSON, manejando arrays de NumPy dentro de la lista
        """
        try:
            lista_limpia = []
            for item in lista:
                if isinstance(item, np.ndarray):
                    # Para arrays dentro de listas (como segmentaciones), manejar de manera especial
                    if item.size < 100:  # Arrays pequeños, convertir a lista
                        lista_limpia.append(item.tolist())
                    else:
                        # Arrays grandes, crear información de metadatos
                        lista_limpia.append({
                            "shape": list(item.shape),
                            "dtype": str(item.dtype),
                            "min": float(item.min()),
                            "max": float(item.max()),
                            "size": int(item.size)
                        })
                elif isinstance(item, dict):
                    lista_limpia.append(self._limpiar_resultados_para_json(item))
                else:
                    lista_limpia.append(item)
            return lista_limpia
        except Exception as e:
            logger.error(f"Error limpiando lista para JSON: {e}")
            return lista

    def _limpiar_resultados_para_json_recursivo(self, obj: Any) -> Any:
        """
        Limpieza recursiva más agresiva para eliminar arrays de NumPy y tipos específicos
        Maneja las máscaras de manera especial para evitar conversión a listas enormes
        """
        if isinstance(obj, np.ndarray):
            # Para máscaras, crear información de metadatos en lugar de convertir a lista
            if obj.size < 100:  # Arrays pequeños, convertir a lista
                return obj.tolist()
            else:
                # Arrays grandes (como máscaras), crear información de metadatos
                return {
                    "shape": list(obj.shape),
                    "dtype": str(obj.dtype),
                    "min": float(obj.min()),
                    "max": float(obj.max()),
                    "size": int(obj.size),
                    "pixels_activos": int(np.sum(obj > 0.5)) if obj.dtype in [np.float32, np.float64] else None
                }
        elif isinstance(obj, (np.float32, np.float64, np.int32, np.int64, np.bool_, np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.uint64)):
            return obj.item()  # Convertir tipos específicos de NumPy a Python nativo
        elif isinstance(obj, dict):
            return {k: self._limpiar_resultados_para_json_recursivo(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._limpiar_resultados_para_json_recursivo(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._limpiar_resultados_para_json_recursivo(item) for item in obj)
        else:
            # Si es un tipo de NumPy que no hemos manejado, intentar convertirlo
            if hasattr(obj, 'item') and hasattr(obj, 'dtype'):
                try:
                    return obj.item()
                except:
                    return str(obj)  # Como último recurso, convertir a string
            return obj

    def liberar_sistema(self):
        """Libera los recursos del sistema de análisis"""
        try:
            if self.sistema_analisis:
                self.sistema_analisis.liberar_sistema()
            
            self.inicializado = False
            logger.info("Sistema de análisis REAL liberado")
            
        except Exception as e:
            logger.error(f"Error liberando sistema REAL: {e}")


# Instancia global del servicio real
servicio_analisis_real = ServicioAnalisisCoplesReal()
