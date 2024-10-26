# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'


from core.factory.PooleadorFactory import PooleadorFactory
from core.products.PooleadorMXProduct import PooleadorMXProduct
from core.products.PooleadorASRProduct import PooleadorASRProduct
from core.products.Pooleador10000Product import Pooleador10000Product
from core.products.PooleadorE320Product import PooleadorE320Product

class PooleadorProductFactory(PooleadorFactory):
    """Clase Concreta para crear pooleadorProduct"""
    
    def crear_pooleador(self, nombre_plugin_pooleador):
        """Metodo para crear un pooleador concreto"""
        match nombre_plugin_pooleador:
            case "obtenerInfoPoolesSNMP_MX.json":
                return PooleadorMXProduct()
            case "obtenerInfoPoolesSNMP_ASR9K.json":
                return PooleadorASRProduct()
            case "obtenerInfoPoolesSNMP_ciscoLegacy_10000.json":
                return Pooleador10000Product()
            case "obtenerInfoPoolesSNMP_juniperLegacyE.json":
                return PooleadorE320Product()
            case _:
                return None

    