# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'

from abc import ABC, abstractmethod

class PooleadorFactory(ABC):
    """Clase Abstracta de pooleador"""
    @abstractmethod
    def crear_pooleador(self, nombre_plugin_pooleador):
        """Metodo para crear un pooleador concreto"""