	# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'

import sys
import re
from utilidades.constantes import MONGO_POOLES_ASR9K_MX
from db.connectionDB import mongoConnection
from loggingConfig import LoggerFileConfig
from constantesPlugins import LOG_CONFIG_FILES
from UtilidadesPooles import *
from ConstantesPooles import *
from utilidadesPlugins import utilidadesPlugins
from core.products.PooleadorProduct import PooleadorProduct
from utilidades.UtilidadesGrafinitum import UtilidadesGrafinitum
from constantes.ConstantesGrafinitum import ConstantesGrafinitum
from abc import ABC, abstractmethod


sys.path.append("/home/ngsop/lilaApp/plugins/utilidadesPlugins")
sys.path.append("/home/ngsop/lilaApp/core")

logger = LoggerFileConfig().crearLogFile(LOG_CONFIG_FILES.get("grafinitum"))

class PooleadorLegacy(PooleadorProduct, ABC):
    """Clase que implementa PooleadorProduct para equipos legacy"""

    def extraer_informacion(self, nombre_equipo, respuesta_equipo):
        """Metodo utilizado para extraer la informacion de los pooles
        configurados en un equipo
        :respuesta_equipo: Se refiere a la respuesta de lila para un equipo
        """
        salida_comando = {}
        try:
            comando = respuesta_equipo.get('comando',"")
            salida_comando = respuesta_equipo['salidaComando'].get(comando, {})
        except KeyError as error_extraer_informcion:
            logger.error(f"Error al extraer información en equipo: {nombre_equipo}: {error_extraer_informcion}")
            titulo = f"GRAFINITUM: error_extraer_informacion en equipo: {nombre_equipo}"
            UtilidadesGrafinitum.enviar_correo_notificacion(self, error_extraer_informcion,titulo)
            return salida_comando #Retornamos la salida del comando como vacio

        return salida_comando