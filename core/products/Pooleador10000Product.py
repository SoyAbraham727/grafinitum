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

class Pooleador10000Product(PooleadorProduct):
    """Clase que implementa PooleadorProduct para equipos legacy 10000"""

    def extraer_informacion(self, respuesta_equipo):
        comando = respuesta_equipo['comando']
        salida_comando = respuesta_equipo['salidaComando'][comando]

        return salida_comando
    
    def construir_informacion(self, db, respuesta_lila, timestamp):
        """Metodo para construir el diccionario de IPV4 de cada equipo
        legacy cisco.
        :param data: respuesta de ejecucion de plugin.
        :return poo_ipv4: Diccionario con información acerca de los poole."""

        pool_ipv4 = {
            'ipv4': {
                'IPV4_TOTAL':{
                    'TOTALES': None,
                    'OCUPADOS': None, 
                    'LIBRES': None
                    }}}
        
        if "C000" not in respuesta_lila["statusCode"]:
            return  # Si no hay código exitoso, no hacemos nada.
        
        try:
            

            # Se obtienen los equipos no encontrados en inventario y los fallidos.
            not_inventory_present = \
                respuesta_lila["response"].pop("notInventoryPresent")
            failed_hosts = respuesta_lila["response"].pop("failed_hosts")

            for equipo in respuesta_lila["response"]:
                for id_comando, info_comando in equipo.items():
                    salida_comando = self.extraer_informacion(info_comando)

                    if salida_comando:
                        suma_pooles_ipv4 = sum(num_pooles for elemento in salida_comando
                                if not any(val == ConstantesGrafinitum.NO_INTERNET for val in elemento.values())
                                for num_pooles in elemento.values() if isinstance(num_pooles, int))
                        
                        if id_comando == '101':
                            pool_ipv4['ipv4']['IPV4_TOTAL']['LIBRES'] = suma_pooles_ipv4
                        elif id_comando == '102':
                            pool_ipv4['ipv4']['IPV4_TOTAL']['OCUPADOS'] = suma_pooles_ipv4

                        pool_ipv4['ipv4']['IPV4_TOTAL']['TOTALES'] += suma_pooles_ipv4

                    else:
                        pool_ipv4 = {
                            'ipv4': {
                                'IPV4_TOTAL':{
                                    'TOTALES': None,
                                    'OCUPADOS': None, 
                                    'LIBRES': None
                                    }}}
                        break


                # Generar el registro
                info_equipo = self.generar_registro_db(
                    timestamp, equipo,
                    pool_ipv4
                )

                # Guardar el registro en la base de datos
                self.guardar_datos(db, info_equipo, 'ipv4')


        except Exception as error_construir_informcion:
            logger.error(f"error_construir_informcion: {error_construir_informcion}")
            pluginMail = PluginMail(to=['jcirilo@uninet.com.mx'],
                        cc=['jcirilo@uninet.com.mx','gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'],
                        html= genHTMLAlert(error_construir_informcion),
                        title="GRAFINITUM: error_construir_informcion",
                                )
            utilidadesPlugins().sendEmailLilaNasBrain(pluginMail)

        return failed_hosts, not_inventory_present