	# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'

from modelsPlugins import PluginExecute

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

    #Identificador de pool NO_INTERNET
    NO_INTERNET = "78.79.95.73.78.84.69.82.78.69.84.1.4.169.254.0.0"

    #Plugins
    pluginExecute_ASR9K = PluginExecute(
                        nameApp='Obtener Info Pooles - SNMP: ASR9K',
                        namePlugin='obtenerInfoPoolesSNMP_ASR9K.json',
                        originPlugin='LOCAL',
                        plugin='obtenerInfoPoolesSNMP_ASR9K.json',
                        idHistorico='',
                        coVer='',
                        usuarioExecute='gmoralea',
                        )

    pluginExecute_MX = PluginExecute(
                        nameApp='Obtener Info Pooles - SNMP: MX',
                        namePlugin='obtenerInfoPoolesSNMP_MX.json',
                        originPlugin='LOCAL',
                        plugin='obtenerInfoPoolesSNMP_MX.json',
                        idHistorico='',
                        coVer='',
                        usuarioExecute='gmoralea',
                        )

    pluginExecute_CISCO_10000 = PluginExecute(
                        nameApp='Obtener Info Pooles - SNMP: Cisco Legacy 10000',
                        namePlugin='obtenerInfoPoolesSNMP_ciscoLegacy_10000.json',
                        originPlugin='LOCAL',
                        plugin='obtenerInfoPoolesSNMP_ciscoLegacy_10000.json',
                        idHistorico='',
                        coVer='',
                        usuarioExecute='gmoralea',
                        )

    pluginExecute_JUNIPER_E320 = PluginExecute(
                        nameApp='Obtener Info Pooles - SNMP: Juniper Legacy E',
                        namePlugin='obtenerInfoPoolesSNMP_juniperLegacyE.json',
                        originPlugin='LOCAL',
                        plugin='obtenerInfoPoolesSNMP_juniperLegacyE.json',
                        idHistorico='',
                        coVer='',
                        usuarioExecute='gmoralea',
                        )