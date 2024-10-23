	# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'

class ConstantesGrafinitum:
    """Clase que define constantes para el manejo de pools en GRAFINITUM."""

    # Nombres de los tipos de pools
    LISTA_NOMBRE_POOLES = ["ipv4", "ipv6", "cgnat"]

    # Claves para los totales de cada tipo de pool
    CLAVES_POOLES_TOTALES = {
        "ipv4": "IPV4_TOTAL",
        "ipv6": "IPV6_TOTAL",
        "cgnat": "CGNAT_TOTAL"
    }

    # Expresiones regulares e identificadores para los tipos de pooles
    IDENTIFICADOR_POOL = {
        "ipv4": [r"^POOL_TELMEX(_\d+)?$"],
        "ipv6": ["LAN_IPV6_TELMEX", "POOL_IPV6_TELMEX"],
        "cgnat": ["CGN_TELMEX", "POOL_CGN"]
    }