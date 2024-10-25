# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'

from utilidadesPlugins import utilidadesPlugins
from abc import ABC, abstractmethod

class PooleadorProduct(ABC):
    """Interfaz de PooleadorProduct"""
    @abstractmethod
    def extraer_informacion(self, nombre_equipo, respuesta_equipo):
        """Metodo para extraer la informacion de la respuesta de lila"""

    @abstractmethod
    def construir_informacion(self, db, respuesta_lila, timestamp):
        """Metodo para construir la informacion de los pooles 
        totales, libres y ocupados"""

