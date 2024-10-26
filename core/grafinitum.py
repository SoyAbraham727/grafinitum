# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'

import sys
import time
import concurrent.futures
import json 
from utilidades.constantes import MONGO_POOLES_ASR9K_MX
from db.connectionDB import mongoConnection
from loggingConfig import LoggerFileConfig
from constantesPlugins import LOG_CONFIG_FILES
from UtilidadesPooles import *
from ConstantesPooles import *
from utilidadesPlugins import utilidadesPlugins
from constantes.ConstantesGrafinitum import ConstantesGrafinitum
from core.factory.PooleadorProductFactory import PooleadorProductFactory

sys.path.append("/home/ngsop/lilaApp/plugins/utilidadesPlugins")
sys.path.append("/home/ngsop/lilaApp/core")

logger = LoggerFileConfig().crearLogFile(LOG_CONFIG_FILES.get("grafinitum"))

def guardar_objeto_como_json(objeto, ruta_archivo):
    """
    Guarda un objeto Python como un archivo JSON en la ruta especificada.

    :param objeto: El objeto Python a guardar.
    :param ruta_archivo: La ruta al archivo JSON donde se guardará el objeto.
    """
    with open(ruta_archivo, 'w') as archivo:
        json.dump(objeto, archivo,indent=2) 

def obtener_info_poles_snmp(timestamp, db, plugin_execute):
    """Obtiene y guarda toda la informacion de los pooles para todos los equipos dsl"""

    logger.info(f"[+] Inicio de ejecucion de plugin: {plugin_execute.nameApp}")

    failed_hosts = {}
    not_inventory_present = {}
    respuesta_lila = None

    try:

        respuesta_lila = utilidadesPlugins().sendPostLiLaExecutor(plugin_execute)
        respuesta_lila = respuesta_lila.json()
        guardar_objeto_como_json(respuesta_lila,f"{plugin_execute.namePlugin}")

        if "C000" in respuesta_lila["statusCode"]:
            pooleador = PooleadorProductFactory().crear_pooleador(plugin_execute.namePlugin)
            failed_hosts, not_inventory_present = pooleador.construir_informacion(db, respuesta_lila, timestamp)

        else:
            logger.warning(f"Se detectó código de error en: {plugin_execute.nameApp}, {respuesta_lila}")

        failed_hosts = respuesta_lila["response"]["failed_hosts"]
        not_inventory_present = respuesta_lila["response"]["not_inventory_present"]
        
        #logger.info("response: %s" % response)
        logger.info(f"[+] Fin de ejecucion de plugin: {plugin_execute.nameApp}")
    
    except Exception as error_obtener_info_poles_snmp:
        logger.error(f"[+] Error en programa obtener_info_poles_snmp {error_obtener_info_poles_snmp}")

    return failed_hosts, not_inventory_present


def main_app():
    """Inicializa y ejecuta los plugins"""

    logger.info("Inicio::mainApp")
    respuesta = {'ASR9K':{},
                 'MX':{},
                 'CISCO_10000': {}, 
                 'JUNIPER_E' : {}} 
    workers_limit = 4

    try:

        inicio = time.time()
        
        plugins = [ConstantesGrafinitum.pluginExecute_ASR9K,
                   ConstantesGrafinitum.pluginExecute_MX,
                   ConstantesGrafinitum.pluginExecute_CISCO_10000,
                   ConstantesGrafinitum.pluginExecute_JUNIPER_E320
                   ]

        mongo_db = mongoConnection(MONGO_POOLES_ASR9K_MX)
        timestamp = int(time.time() * 1000)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers_limit)

        futures = {executor.submit(obtener_info_poles_snmp, timestamp, mongo_db, plugin):
                   plugin for plugin in plugins}
                            
        concurrent.futures.wait(futures)

        logger.info(f"futures: {futures}")

        count = 0
        for numFuture in futures:
            match count:
                case 0:
                    respuesta.update({'ASR9K': numFuture.result()})
                case 1:
                    respuesta.update({'MX': numFuture.result()})
                case 2:
                    respuesta.update({'CISCO_10000': numFuture.result()})
                case 3:
                    respuesta.update({'JUNIPER_E': numFuture.result()})
                case _:
                    logger.warning("numFuture inválido")
            count += 1

        logger.info(f"respuesta: {respuesta}")

        fin = time.time()

    except Exception as error_main_plugin:
        logger.error(f"Error::Se ha generado una excepción::mainApp:: {error_main_plugin}")
        raise Exception(f"Error::Se ha generado una excepción::mainApp:: {error_main_plugin}")
    finally:
        if mongo_db:
            mongo_db.close()
        if executor:
            executor.shutdown()
        logger.info(f"Fin::Tiempo de ejecución de mainApp: {str(fin-inicio)}")

if __name__ == "__main__":
    main_app()
