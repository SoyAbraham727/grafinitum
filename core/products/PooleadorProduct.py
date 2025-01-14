# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'

from abc import ABC, abstractmethod

class PooleadorProduct(ABC):
    """Interfaz de PooleadorProduct"""
    @abstractmethod
    def extraer_informacion(self, nombre_equipo, info_equipo):
        """Método para extraer la información de la respuesta de lila para un equipo.

        :param nombre_equipo: Nombre del equipo del que se extraera la informacion.
        :param info_equipo: Salida de los comandos ejecutados en un equipo.
        :returns Pooles homologados: Pooles homologados con pooles totales, libres y ocupados.
        """

    @abstractmethod
    def construir_informacion(self, db, respuesta_lila, timestamp):
        """Método para construir la información de los pooles (ipv4,ipv6,cgnat) totales, 
        libres y ocupados por equipo.

        :param db: Instancia de conexion a la base de datos.
        :param respuesta_lila: Respuesta de lila al ejecutar un plugin.
        :param timestamp: Valor numerico para representar la hora de ejecucion.
        :returns failed_hosts, not_inventory_present: donde failed_host se refiere a los equipos que no puedieron ser ejecutados
        y not_inventory_present a los equipos que no se encontraron en el inventario"""
