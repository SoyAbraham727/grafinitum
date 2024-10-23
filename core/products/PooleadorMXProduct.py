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


sys.path.append("/home/ngsop/lilaApp/plugins/utilidadesPlugins")
sys.path.append("/home/ngsop/lilaApp/core")

logger = LoggerFileConfig().crearLogFile(LOG_CONFIG_FILES.get("grafinitum"))

class PooleadorMXProduct(PooleadorProduct):
    """Clase concreta de pooleador"""

    def homologar_pooles(self, pooles, totales, ocupados):
         """Metodo para homologar la informacion de los pooles configurados"""

         pooles_homologados = {}

         for pool in ConstantesGrafinitum.LISTA_NOMBRE_POOLES:
            if pooles.get(pool):
                for oid, nombre_pool in pooles[pool].items():
                    pooles_totales = totales.get(oid,None)
                    pooles_ocupados = ocupados.get(oid,None)

                    if pooles_totales is not None and \
                        pooles_ocupados is not None:
                        pooles_libres = pooles_totales - pooles_ocupados
                    else:
                        pooles_totales = pooles_ocupados = pooles_libres = None

                    pooles_homologados[nombre_pool] = {
                        "TOTALES": pooles_totales,
                        "OCUPADOS": pooles_ocupados,
                        "LIBRES": pooles_libres
                    }
                pooles[pool].update(pooles_homologados)


    def extraer_informacion(self, equipo):
        """Metodo para extraer la informacion de la respuesta de lila"""

        pooles = { "ipv4": {}, "ipv6": {}, "cgnat": {}}
            
        try:
            
            totales = equipo["102"]["salidaComando"]
            ocupados = equipo["103"]["salidaComando"]
        
            resultados = equipo["101"].get("resultadosValidacion", {})
            pooles["ipv4"] = resultados.get("(NO_INTERNET|POOL_TELMEX)", {})
            pooles["ipv6"] = resultados.get("IPV6", {})
            pooles["cgnat"] = resultados.get("CGN", {})

            self.homologar_pooles(pooles, totales, ocupados)

        except Exception as error_extraer_informacion:
            logger.error(f"error_extraer_informacion: \
                                                {error_extraer_informacion}")
            UtilidadesGrafinitum.enviarCorreoNotificacion(
                error_extraer_informacion
            )
        
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


    def generar_registro_db(self, timestamp, equipo, pooles):
        """Metodo para generar el registro completo por equipo"""

        return { "timestamp":timestamp, "device":equipo, "data":pooles }
        
        
    def construir_informacion(self, db, respuesta_lila, timestamp):
        """Metodo para construir la informacion de los pooles totales, l
        ibres y ocupados por equipo"""

        #C000 - codigo de estado exitoso de lila
        if "C000" in respuesta_lila["statusCode"]:
            #Se obtienen los equipos no encontrados en inventario.
            not_inventory_present \
                = respuesta_lila["response"].pop("notInventoryPresent")
            #Se obtienen los equipos fallidos.
            failed_host = respuesta_lila["response"].pop("failed_hosts")

            for equipo in respuesta_lila["response"]:
                pooles = self.extraer_informacion(equipo)
                
                for pool_name in ConstantesGrafinitum.LISTA_NOMBRE_POOLES:
                    if pooles[pool_name]:

                        self.calcular_pooles_totales(
                            pooles, 
                            ConstantesGrafinitum.IDENTIFICADOR_POOL[pool_name], 
                            pool_name
                            )
                        
                        info_equipo = self.generar_registro_db(
                            timestamp, 
                            equipo, 
                            pooles[pool_name]
                            )
                        
                        self.guardar_data(db, info_equipo, pool_name)

                                        