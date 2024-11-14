	# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'

import sys
sys.path.append("/home/ngsop/lilaApp/plugins/utilidadesPlugins")
sys.path.append("/home/ngsop/lilaApp/core")
sys.path.append("/home/ngsop/lilaApp/plugins/scripts/grafinitum_backend")
from utilidades.loggingConfig import LoggerFileConfig
from constantesPlugins import LOG_CONFIG_FILES
from core.products.PooleadorLegacy import PooleadorLegacy
from utilidades.UtilidadesGrafinitum import UtilidadesGrafinitum
from constantes.ConstantesGrafinitum import ConstantesGrafinitum
from datetime import datetime, timezone

logger = LoggerFileConfig().crearLogFile(LOG_CONFIG_FILES.get("grafinitum"))

class Pooleador10000Product(PooleadorLegacy):
    """Clase que implementa PooleadorProduct para equipos legacy 10000."""

    def construir_informacion(self, db, respuesta_lila, timestamp):
        """Metodo para construir el diccionario de IPV4 de cada equipolegacy cisco.

        :param db: Instancia de conexion a la base de datos.
        :param respuesta_lila: Respuesta de lila al ejecutar un plugin
        :param timestamp: Valor numerico para representar la hora de ejecucion
        :returns failed_hosts, not_inventory_present: Donde failed_host se refiere a los equipos que no puedieron ser ejecutados
        y not_inventory_present a los equipos que no se encontraron en el inventario"""

        pool_ipv4_inicial = {'ipv4': {'IPV4_TOTAL':{'TOTALES': 0,'OCUPADOS': 0, 'LIBRES': 0}}}
        pool_ipv4_none = {'ipv4': {'IPV4_TOTAL':{'TOTALES': None,'OCUPADOS': None, 'LIBRES': None}}}
        pool_ipv4 = pool_ipv4_inicial.copy()
        
        # Se obtienen los equipos no encontrados en inventario y los fallidos.
        #not_inventory_present = respuesta_lila["response"].pop("notInventoryPresent")
        respuesta_lila["response"].pop("notInventoryPresent")
        failed_hosts = respuesta_lila["response"].pop("failed_hosts")
        incomplete_hosts = {}
        

        for nombre_equipo, info_equipo in respuesta_lila["response"].items():
            registro_equipo = {nombre_equipo:"OK"}
            try:
                for id_comando, info_comando in info_equipo.items():
                    salida_comando = self.extraer_informacion(nombre_equipo, info_comando)

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
                        pool_ipv4 = pool_ipv4_none.copy()
                        registro_equipo = {nombre_equipo:"Incomplete data"}
                        incomplete_hosts.update(registro_equipo)
                        break

                logger.warning(f"info Equipo:::{registro_equipo}")
                # Generar el registro
                registro = UtilidadesGrafinitum.generar_registro(self,timestamp, registro_equipo, pool_ipv4['ipv4'])

                # Guardar el registro en la base de datos
                db.saveData(registro, 'ipv4') #Se elimina la llamada a los metodos

                pool_ipv4 = pool_ipv4_inicial.copy()


            except Exception as error_construir_informcion:
                logger.error(f"Error al construir informacion del equipo {nombre_equipo}: {error_construir_informcion}")
                titulo = f"GRAFINITUM: error_construir_informacion de equipo: {nombre_equipo}"
                UtilidadesGrafinitum.enviar_correo_notificacion(self, error_construir_informcion,titulo)
        if failed_hosts:
            failed_hosts = UtilidadesGrafinitum.crear_failed_hosts_hashset(self, failed_hosts)
            UtilidadesGrafinitum.construir_informacion_equipos_fallidos_legacy(self, failed_hosts, timestamp, db)

        return failed_hosts, incomplete_hosts
