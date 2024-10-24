# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'

from utilidadesPlugins import utilidadesPlugins
from abc import ABC, abstractmethod

class PooleadorProduct(ABC):
    """Clase Abstracta de pooleador"""
    @abstractmethod
    def extraer_informacion(self, respuesta_equipo):
        """Metodo para extraer la informacion de la respuesta de lila"""

    @abstractmethod
    def construir_informacion(self, db, respuesta_lila, timestamp):
        """Metodo para construir la informacion de los pooles 
        totales, libres y ocupados"""

    def ejecutar_plugin(self, plugin_execute):
        """Metodo para ejecutar plugin y devolver la respuesta en formato 
        json"""
        respuesta_lila = utilidadesPlugins().sendPostLiLaExecutor(plugin_execute)
        respuesta_lila = respuesta_lila.json()

        return respuesta_lila
    
    def guardar_datos(self, db, registro, coleccion):
        """Metodo para guardar la informacion en la base de datos"""
        db.saveData(registro, coleccion)

    def generar_registro_db(self, timestamp, equipo, info_pooles):
        """Metodo para generar el registro completo por equipo"""

        return { "timestamp":timestamp, "device":equipo, "data":info_pooles }