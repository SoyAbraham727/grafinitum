	# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'


import re
import sys
sys.path.append("/home/ngsop/lilaApp/core")
sys.path.append("/home/ngsop/lilaApp/plugins/scripts/grafinitum_backend")
sys.path.append("/home/ngsop/lilaApp/plugins/utilidadesPlugins")
from utilidades.loggingConfig import LoggerFileConfig
from constantesPlugins import LOG_CONFIG_FILES
from core.products.PooleadorProduct import PooleadorProduct
from utilidades.UtilidadesGrafinitum import UtilidadesGrafinitum
from constantes.ConstantesGrafinitum import ConstantesGrafinitum

from abc import ABC, abstractmethod



logger = LoggerFileConfig().crearLogFile(LOG_CONFIG_FILES.get("grafinitum"))

class PooleadorNextGeneration(PooleadorProduct, ABC):
    """Clase Abstracta de pooleadorProduct"""

    @abstractmethod
    def homologar_pooles(self, pooles, info_pool1, info_pool2):
         """Metodo para homologar la informacion de los pooles configurados"""


    def extraer_informacion(self, nombre_equipo, info_equipo):
        """Método para extraer la información de la respuesta de lila para un equipo
        :nombre_equipo: Es el nombre del equipo
        :info_equipo: Es la salida de los comandos ejecutados en un equipo.
        """
        
        pooles = {"ipv4": {}, "ipv6": {}, "cgnat": {}}
        
        try:
            validaciones = info_equipo["101"].get("resultadosValidacion", {})
            totales = info_equipo["102"].get("salidaComando", {})
            ocupados = info_equipo["103"].get("salidaComando", {})

            pooles["ipv4"] = validaciones.get("(NO_INTERNET|POOL_TELMEX)", {})
            pooles["ipv6"] = validaciones.get("IPV6", {})
            pooles["cgnat"] = validaciones.get("CGN", {})

            self.homologar_pooles(pooles, totales, ocupados)

        except KeyError as error_extraer_informcion:
            logger.error(f"Error al extraer información en equipo: {nombre_equipo}: {error_extraer_informcion}")
            titulo = f"GRAFINITUM: error_extraer_informacion en equipo: {nombre_equipo}"
            UtilidadesGrafinitum.enviar_correo_notificacion(self, error_extraer_informcion,titulo)
            
            return pooles  # Retorna pooles vacíos en caso de error

        return pooles
    

    def calcular_pooles_totales(self, pooles, identificadores, nombre_pool):
        """Funcion para calcular pooles totales por equipo"""

        totales = {"TOTALES": None, "OCUPADOS": None, "LIBRES": None}
        try:
            for pool_nombre, pool_valores in pooles[nombre_pool].items():
                if any(re.match(patron, pool_nombre) for patron in identificadores):
                    for key in ["TOTALES", "OCUPADOS", "LIBRES"]:
                        valor_actual = pool_valores.get(key)
                        
                        if valor_actual is not None and totales[key] is not None:
                            totales[key] += valor_actual
                        elif valor_actual is not None and totales[key] is None:
                            totales[key] = valor_actual
                        

            pooles[nombre_pool].update({
                ConstantesGrafinitum.CLAVES_POOLES_TOTALES[nombre_pool]: totales
            })
        except Exception as e:
            logger.error(f"Error al calcular pooles totales para {nombre_pool}: {e}")

        return dict(pooles)

    def construir_informacion(self, db, respuesta_lila, timestamp):
        """Método para construir la información de los pooles (ipv4,ipv6,cgnat) totales, 
        libres y ocupados por equipo.
        :param db: Instancia de conexion a la base de datos.
        :respuesta_lila: Es la respuesta de lila al ejecutar un plugin
        :timestamp: Valor numerico para representar la hora de ejecucion
        :return failed_hosts, not_inventory_present: Donde failed_host se refiere a los equipos que no puedieron ser ejecutados
        y not_inventory_present a los equipos que no se encontraron en el inventario"""

        # Se obtienen los equipos no encontrados en inventario y los fallidos.
        not_inventory_present = respuesta_lila["response"].pop("notInventoryPresent",[])
        failed_hosts = respuesta_lila["response"].pop("failed_hosts",[])

        for nombre_equipo, info_equipo in respuesta_lila["response"].items(): #Se corrige
            logger.info(f"Inicia :: construir_informacion :: para el equipo: {nombre_equipo}")
            try:
                pooles = self.extraer_informacion(nombre_equipo, info_equipo)#Se corrige error
                
                for pool_name in ConstantesGrafinitum.LISTA_NOMBRE_POOLES:
                    if pooles.get(pool_name):

                        # Calcular los pools totales
                        self.calcular_pooles_totales(
                            pooles,
                            ConstantesGrafinitum.IDENTIFICADOR_POOL[pool_name],
                            pool_name
                        )
                        
                        # Generar el registro
                        registro = { "timestamp":timestamp, "device":nombre_equipo, "data":pooles[pool_name] } #Se elimina la llamada a los metodos, se realiza en código
                        logger.info(f"REGISTRO DB :::: {registro}")
                        
                        # Guardar el registro en la base de datos
                        #db.saveData(registro, pool_name) #Se elimina la llamada a los metodos

            except Exception as error_construir_informcion:
                logger.error(f"Error al construir informacion del equipo {nombre_equipo}: {error_construir_informcion}")
                titulo = f"GRAFINITUM: error_construir_informacion de equipo: {nombre_equipo}"
                UtilidadesGrafinitum.enviar_correo_notificacion(self, error_construir_informcion,titulo)
            
        return failed_hosts, not_inventory_present

                                        