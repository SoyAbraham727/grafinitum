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

class PooleadorLatestVersion(PooleadorProduct, ABC):
    """Clase concreta de pooleador para Juniper MX"""

    @abstractmethod
    def homologar_pooles(self, pooles, info_pool1, info_pool2):
         """Metodo para homologar la informacion de los pooles configurados"""


    def extraer_informacion(self, respuesta_equipo):
        """Metodo para extraer la informacion de la respuesta de lila"""

        pooles = { "ipv4": {}, "ipv6": {}, "cgnat": {}}
            
        validaciones = respuesta_equipo["101"].get("resultadosValidacion", {})
        totales = respuesta_equipo["102"].get("salidaComando", {})
        ocupados = respuesta_equipo["103"].get("salidaComando", {})

        pooles["ipv4"] = validaciones.get("(NO_INTERNET|POOL_TELMEX)", {})
        pooles["ipv6"] = validaciones.get("IPV6", {})
        pooles["cgnat"] = validaciones.get("CGN", {})

        
        self.homologar_pooles(pooles, totales, ocupados)

        return pooles
    

    def calcular_pooles_totales(self, pooles, identificadores, nombre_pool):
        """Funcion para calcular pooles totales por equipo"""

        totales = {"TOTALES": None, "OCUPADOS": None, "LIBRES": None}

        for pool_nombre, pool_valores in pooles[nombre_pool].items():
            if any(re.match(patron, pool_nombre) for patron in identificadores):
                for key in ["TOTALES", "OCUPADOS", "LIBRES"]:
                    valor_actual = pool_valores.get(key)

                    if valor_actual is not None:
                        if totales[key] is None:
                            totales[key] = valor_actual
                        else:
                            totales[key] += valor_actual

        pooles[nombre_pool].update({
            ConstantesGrafinitum.CLAVES_POOLES_TOTALES[nombre_pool]: totales
        })

        return dict(pooles)

    def construir_informacion(self, db, respuesta_lila, timestamp):
        """Método para construir la información de los pools totales, 
        libres y ocupados por equipo."""
        
        # C000 - código de estado exitoso de Lila
        if "C000" not in respuesta_lila["statusCode"]:
            return  None, None # Si no hay código exitoso, retornamos listas vacias

        # Se obtienen los equipos no encontrados en inventario y los fallidos.
        not_inventory_present = \
            respuesta_lila["response"].pop("notInventoryPresent",[])
        failed_hosts = respuesta_lila["response"].pop("failed_hosts",[])

        for equipo in respuesta_lila["response"]:
            pooles = self.extraer_informacion(equipo)
            
            for pool_name in ConstantesGrafinitum.LISTA_NOMBRE_POOLES:
                if pooles.get(pool_name):  # Usa .get() para evitar KeyError.

                    # Calcular los pools totales
                    self.calcular_pooles_totales(
                        pooles,
                        ConstantesGrafinitum.IDENTIFICADOR_POOL[pool_name],
                        pool_name
                    )
                    
                    # Generar el registro
                    info_equipo = self.generar_registro_db(
                        timestamp, equipo,
                        pooles[pool_name]
                    )

                    # Guardar el registro en la base de datos
                    self.guardar_datos(db, info_equipo, pool_name)
        return failed_hosts, not_inventory_present

                                        