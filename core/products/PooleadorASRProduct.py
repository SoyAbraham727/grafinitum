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
from core.products.PooleadorNextGeneration import PooleadorNextGeneration
from utilidades.UtilidadesGrafinitum import UtilidadesGrafinitum
from constantes.ConstantesGrafinitum import ConstantesGrafinitum


sys.path.append("/home/ngsop/lilaApp/plugins/utilidadesPlugins")
sys.path.append("/home/ngsop/lilaApp/core")

logger = LoggerFileConfig().crearLogFile(LOG_CONFIG_FILES.get("grafinitum"))

class PooleadorASRProduct(PooleadorNextGeneration):
    """Clase concreta de pooleador para Cisco ASR9K"""

    def homologar_pooles(self, pooles,info_pool1, info_pool2):
        """Metodo para homologar la informacion de los pooles configurados
        :pooles: Son los pooles configurados en un equipo
        :info_pool1: Se refiere a la cantidad de pooles ocupados
        :info_pool2: Se refiere a la cantidad de pooles libres
        """
        
        pooles_homologados = {}

        for pool in ConstantesGrafinitum.LISTA_NOMBRE_POOLES:
            if pooles.get(pool):
                for oid, nombre_pool in pooles[pool].items():
                    pooles_ocupados = info_pool1.get(oid,None)
                    pooles_libres = info_pool2.get(oid,None)

                    if pooles_ocupados is not None and \
                        pooles_libres is not None:
                        pooles_totales = pooles_ocupados + pooles_libres
                    else:
                        pooles_ocupados = pooles_totales = pooles_libres = None

                    pooles_homologados[nombre_pool] = {
                        "TOTALES": pooles_totales,
                        "OCUPADOS": pooles_ocupados,
                        "LIBRES": pooles_libres
                    }
                pooles[pool].update(pooles_homologados)