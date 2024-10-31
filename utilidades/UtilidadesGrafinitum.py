# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'

import sys
# Añadir rutas al sistema
sys.path.append("/home/ngsop/lilaApp/plugins/utilidadesPlugins")
sys.path.append("/home/ngsop/lilaApp/core")
sys.path.append("/home/ngsop/lilaApp/plugins/scripts/grafinitum_backend")
import json
import html
import dominate

# Importar módulos personalizados
from loggingConfig import LoggerFileConfig
from constantesPlugins import LOG_CONFIG_FILES
from modelsPlugins import PluginMail
from utilidadesPlugins import utilidadesPlugins
from dominate.tags import *
from constantes.ConstantesGrafinitum import ConstantesGrafinitum
from datetime import datetime, timezone


# Configuración del logger
logger = LoggerFileConfig().crearLogFile(LOG_CONFIG_FILES.get("grafinitum"))

class UtilidadesGrafinitum:
    """Clase de Utilidades para Grafinitum."""

    def gen_html_alert(self, exception):
        """Genera una alerta en formato HTML.
        
        :param exception: Mensaje de error que se mostrara en el correo enviado.
        """
        logger.info("inicio::genHTMLAlert:GRAFINITUM")
        try:
            format = datetime.today().strftime('%Y-%m-%d %H:%M')
            doc = dominate.document(title='GRAFINITUM')

            # Leer el archivo CSS
            with open("/home/ngsop/lilaApp/plugins/scripts/monTelcel/style.css") as cssFile:
                css_info = cssFile.read()

            # Construir el documento HTML
            with doc.head:
                style(css_info)
            with doc:
                h1("GRAFINITUM: Detección de Excepciones " + html.unescape("&#9888;"),
                   align="center", style="color:red;")
                
                with table(id="customers"):
                    with tr():
                        th("Estado")
                        th("Descripción")
                        th("Hora de ejecución")
                    with tr():
                        td("Revisión ejecutada")
                        td(str(exception))
                        td(format)
                br()
                with div():
                    h3(i("Atentamente, Gerencia de Soluciones Operativas (GSOP)"))

            logger.info("fin::genHTMLAlert:GRAFINITUM")
            return doc.render()

        except Exception as error_gen_html_alert:
            logger.error(f"errorGenHTMLAlert: {error_gen_html_alert}")
            return ""

    def enviar_correo_notificacion(self, exception, titulo):
        """Envía una notificación por correo con el mensaje especificado.
        
        :param exception: Mensaje de error que se mostrara en el correo enviado.
        :param titulo: Mensaje mostrado en el asunto del correo.
        """
        
        try:
            # Crear el objeto de correo
            pluginMail = PluginMail(
                to=['jcirilo@uninet.com.mx', 
                    'jbarranc@uninet.com.mx', 
                    'gmoralea@uninet.com.mx'
                    ],
                cc=[
                    'jcirilo@uninet.com.mx', 
                    'jbarranc@uninet.com.mx', 
                    'gmoralea@uninet.com.mx'
                    ],
                html=self.gen_html_alert(exception),
                title= titulo
            )

            # Enviar el correo
            utilidadesPlugins().sendEmailLilaNasBrain(pluginMail)
        except Exception as e:
            logger.error(f"Error al enviar correo: {e}")

    def generar_pipeline_consulta_pooles(self, nombre_equipo, clave):
        """Metodo para generar el pipeline para realizar la consulta a la base de datos.
        
        :param nombre_equipo: Nombre del equipo a consultar.
        :param clave: Clave de los valores totales.

        :returns pipeline: Pipeline para realizar la consulta
        """
        pipeline = [
            {
                "$match": {
                    "device": nombre_equipo,
                    clave: {"$ne": None}
                }
            },
            {
                "$project": {
                    clave: 1,
                    "_id": 0
                }
            },
            {
                "$limit": 1
            }
        ]

        return pipeline


    def crear_failed_hosts_hashset(self, failed_hosts):
        """Metodo que realiza un set para obtener la lista de equipos no duplicados.
        
        :param failed_host: Lista de diccionarios con los equipos fallidos.
        :returns equipos_unicos: Lista de equipos no duplicados
        """

        unique_failed_hosts = set()

        for host_dict in failed_hosts:
            for host, message in host_dict.items():
                unique_failed_hosts.add(json.dumps({host: message})) 
        equipos_unicos = [json.loads(host) for host in unique_failed_hosts]
        return equipos_unicos
    
    def obtener_pooles_configurados(self, db, nombre_equipo):
        """Metodo para obtener los pooles configurados en un equipo, de acuerdo a los registros de la base de datos.
        
        :param db: Instancia de conexion a la base de datos.
        :param nombre_equipo: Nombre del equipo que sera consultado.
        :returns pooles: Lista de pooles configurados en un equipo.
        """
        pooles = []
        for coleccion in ConstantesGrafinitum.LISTA_NOMBRE_POOLES:
            clave = f"data.{ConstantesGrafinitum.CLAVES_POOLES_TOTALES[coleccion]}.TOTALES"
            pipeline = UtilidadesGrafinitum.generar_pipeline_consulta_pooles(self, nombre_equipo,clave)

            response = db.consultaAgregacion(pipeline, coleccion)
            
            if response:
                logger.info(f"{nombre_equipo} :: Se encontro registro no nulo en {coleccion}\nRegistro encontrado: {response}")
                pooles.append(coleccion)
            else:
                logger.info(f"{nombre_equipo} :: No se encontro ningun registro no nulo en {coleccion}, no se guardara informacion el la DB")

        return pooles


    def construir_informacion_equipos_fallidos_next_generation(self, failed_hosts, timestamp, db):
        """Metodo que construye el registro de la base de datos con valores nulos de un equipo Next Generation.
        
        :param failed_host: Lista de diccionarios con los equipos fallidos.
        :param timestamp: Valor numerico que representa la hora y fecha de ejecucion.
        :param db: Instancia de conexion a la base de datos.
        """
        for info_equipo in failed_hosts:
            for nombre_equipo in info_equipo.keys():        
                logger.info("inicia :: obtener pooles equipos fallidos NextGen")        
                pooles = UtilidadesGrafinitum.obtener_pooles_configurados(self, db, nombre_equipo)
                logger.info("termina :: obtener pooles equipos fallidos NextGen")
                for pool in pooles:
                    registro = UtilidadesGrafinitum.generar_registro(self, timestamp, nombre_equipo, ConstantesGrafinitum.POOLES_NULOS[pool])
                    logger.warning(f"EQUIPO FALLIDO: {nombre_equipo}\nREGISTRO DB:: {pool} ::: {registro}")
                    db.saveData(registro, pool)
    
    def construir_informacion_equipos_fallidos_legacy(self, failed_hosts, timestamp, db):
        """Metodo que construye el registro de la base de datos con valores nulos de un equipo Legacy.
        
        :param failed_host: Lista de diccionarios con los equipos fallidos.
        :param timestamp: Valor numerico que representa la hora y fecha de ejecucion.
        :param db: Instancia de conexion a la base de datos.
        """
        for info_equipo in failed_hosts:
            for nombre_equipo in info_equipo.keys():
                pool = "ipv4"
                registro = UtilidadesGrafinitum.generar_registro(self, timestamp, nombre_equipo, ConstantesGrafinitum.POOLES_NULOS[pool])
                logger.warning(f"EQUIPO FALLIDO: {nombre_equipo}\nREGISTRO DB:: {pool} ::: {registro}")
                db.saveData(registro, pool)

    def generar_registro(self, timestamp, nombre_equipo,datos_pooleo):
        registro = {
                    "timestamp":timestamp, 
                    "device":nombre_equipo, 
                    "data":datos_pooleo,
                    "timestampDate": datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
                }
        return registro
        
