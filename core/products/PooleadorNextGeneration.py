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
from datetime import datetime, timezone

from abc import ABC, abstractmethod



logger = LoggerFileConfig().crearLogFile(LOG_CONFIG_FILES.get("grafinitum"))

class PooleadorNextGeneration(PooleadorProduct, ABC):
    """Clase Abstracta de pooleadorProduct."""

    @abstractmethod
    def homologar_pooles(self, pooles, info_pool1, info_pool2):
         """Metodo para homologar la informacion de los pooles configurados."""


    def actualizar_oid (self, diccionario):
        """Metodo que actualiza el diccionario con el ultimo valor en su key (oid).

        :param diccionario: Diccionario al cual se le cambiara el valor de su oid.
        :returns diccionario_actualizado: Diccionario con sus oids actualizadas.
        """
        diccionario_actualizado = {oid.split(".")[-1] : valor for oid, valor in diccionario.items()}

        return diccionario_actualizado

    def extraer_informacion(self, nombre_equipo, info_equipo):
        """Método para extraer la información de la respuesta de lila para un equipo.

        :param nombre_equipo: Nombre del equipo del que se extraera la informacion.
        :param info_equipo: Salida de los comandos ejecutados en un equipo.
        :returns Pooles homologados: Pooles homologados con pooles totales, libres y ocupados.
        """
        
        pooles = {"ipv4": {}, "ipv6": {}, "cgnat": {}}
        pooles_homologados = {"ipv4": {}, "ipv6": {}, "cgnat": {}}

        try:
            validaciones = info_equipo["101"].get("resultadosValidacion", {})
            pooles.update({
                "ipv4": self.actualizar_oid(validaciones.get("(NO_INTERNET|POOL_TELMEX)", {})),
                "ipv6": self.actualizar_oid(validaciones.get("IPV6", {})),
                "cgnat": self.actualizar_oid(validaciones.get("CGN", {}))
            })
            
            totales = self.actualizar_oid(info_equipo["102"].get("salidaComando", {}))
            ocupados = self.actualizar_oid(info_equipo["103"].get("salidaComando", {}))

            pooles_homologados = self.homologar_pooles(pooles, totales, ocupados)

        except KeyError as error_extraer_informcion:
            logger.error(f"Error al extraer información en equipo: {nombre_equipo}: {error_extraer_informcion}")
            titulo = f"GRAFINITUM: error_extraer_informacion en equipo: {nombre_equipo}"
            UtilidadesGrafinitum.enviar_correo_notificacion(self, error_extraer_informcion,titulo)
            
            return pooles_homologados  # Retorna pooles vacíos en caso de error

        return pooles_homologados
    

    def calcular_pooles_totales(self, pooles, identificadores, nombre_pool):
        """Funcion para calcular pooles totales por equipo.

        :param pooles: Diccionario de pooles.
        :param identificadores: Usados para identificar el tipo de pool.
        :param nombre_pool: ipv4, ipv6, cgnat.
        :returns pooles: Diccionario de pooles con la suma total.
        """
                                
        totales = {"TOTALES": None, "OCUPADOS": None, "LIBRES": None}
        totales_none = totales.copy()
        calculo_exitoso = True
        try:
            for pool_nombre, pool_valores in pooles[nombre_pool].items():
                if any(re.match(patron, pool_nombre) for patron in identificadores):
                    for key in ["TOTALES", "OCUPADOS", "LIBRES"]:
                        valor_actual = pool_valores.get(key)
                        
                        if valor_actual is not None and totales[key] is not None:
                            totales[key] += valor_actual
                        elif valor_actual is not None and totales[key] is None:
                            totales[key] = valor_actual
                        else:
                            calculo_exitoso = False
                            totales = totales_none.copy()
                            break
                if not calculo_exitoso:
                    break

            pooles[nombre_pool].update({
                ConstantesGrafinitum.CLAVES_POOLES_TOTALES[nombre_pool]: totales
            })
        except Exception as e:
            logger.error(f"Error al calcular pooles totales para {nombre_pool}: {e}")

        return calculo_exitoso

    def construir_informacion(self, db, respuesta_lila, timestamp):
        """Método para construir la información de los pooles (ipv4,ipv6,cgnat) totales, 
        libres y ocupados por equipo.

        :param db: Instancia de conexion a la base de datos.
        :param respuesta_lila: Respuesta de lila al ejecutar un plugin.
        :param timestamp: Valor numerico para representar la hora de ejecucion.
        :returns failed_hosts, not_inventory_present: donde failed_host se refiere a los equipos que no puedieron ser ejecutados
        y not_inventory_present a los equipos que no se encontraron en el inventario"""

        # Se obtienen los equipos no encontrados en inventario y los fallidos.
        #not_inventory_present = respuesta_lila["response"].pop("notInventoryPresent",[])
        respuesta_lila["response"].pop("notInventoryPresent",[])
        failed_hosts = respuesta_lila["response"].pop("failed_hosts",[])
        incomplete_hosts = {}

        for nombre_equipo, info_equipo in respuesta_lila["response"].items(): #Se corrige
            try:
                pooles = self.extraer_informacion(nombre_equipo, info_equipo)#Se corrige error
                for pool_name in ConstantesGrafinitum.LISTA_NOMBRE_POOLES:
                    if pooles.get(pool_name):

                        # Calcular los pools totales
                        calculo_exitoso = self.calcular_pooles_totales(
                            pooles,
                            ConstantesGrafinitum.IDENTIFICADOR_POOL[pool_name],
                            pool_name
                        )
                        #Se asigna status dependiendo del resultado del calculo total
                        info_equipo = {nombre_equipo: "OK" if calculo_exitoso else "Incomplete data"}
                        if info_equipo.get(nombre_equipo) == "Incomplete data":
                            incomplete_hosts.update(info_equipo)

                            
                        # Generar el registro
                        registro = UtilidadesGrafinitum.generar_registro(self,timestamp, info_equipo, pooles[pool_name])
                        # Guardar el registro en la base de datos
                        db.saveData(registro, pool_name) #Se elimina la llamada a los metodos
                    else:

                        #se verifica si existe el historico del pool
                        pool_configurado = UtilidadesGrafinitum.obtener_pooles_configurados(self, db, nombre_equipo, [pool_name])
                        
                        if pool_configurado:
                            logger.error(f"pool configurado {pool_configurado}")
                            #Se crea status de pooleo no configurado
                            info_equipo = {nombre_equipo: "No configurado"}
                            # Generar el registro
                            registro = UtilidadesGrafinitum.generar_registro(self,timestamp, info_equipo, ConstantesGrafinitum.POOLES_NULOS[pool_name])

                            logger.error(f"No configurado:: {pool_name}, REGISTRO:: {registro}")
                            # Guardar el registro en la base de datos
                            db.saveData(registro, pool_name)

            except Exception as error_construir_informacion:
                logger.error(f"Error al construir informacion del equipo {nombre_equipo}: {error_construir_informacion}")
                titulo = f"GRAFINITUM: error_construir_informacion de equipo: {nombre_equipo}"
                UtilidadesGrafinitum.enviar_correo_notificacion(self, error_construir_informacion,titulo)
        if failed_hosts:
            failed_hosts = UtilidadesGrafinitum.crear_failed_hosts_hashset(self, failed_hosts)
            UtilidadesGrafinitum.construir_informacion_equipos_fallidos_next_generation(self, failed_hosts, timestamp, db)

        return failed_hosts, incomplete_hosts

                                        


                                        
