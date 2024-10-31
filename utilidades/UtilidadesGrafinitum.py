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
from datetime import datetime
from constantes.ConstantesGrafinitum import ConstantesGrafinitum



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
                to=['jcirilo@uninet.com.mx'],
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
    
        unique_failed_hosts = set()

        for host_dict in failed_hosts:
            for host, message in host_dict.items():
                unique_failed_hosts.add(json.dumps({host: message})) 

        return [json.loads(host) for host in unique_failed_hosts]
    
    def obtener_pooles_configurados(self, db, nombre_equipo):
        pooles = []
        for coleccion in ConstantesGrafinitum.LISTA_NOMBRE_POOLES:
            clave = f"data.{ConstantesGrafinitum.CLAVES_POOLES_TOTALES[coleccion]}.TOTALES"
            pipeline = UtilidadesGrafinitum.generar_pipeline_consulta_pooles(self, nombre_equipo,clave)

            response = db.consultaAgregacion(pipeline, coleccion)
            
            logger.info(f"{coleccion} :: response: {response}")
            if response:
                pooles.append(coleccion)

        return pooles


    def construir_informacio_equipos_fallidos_NextGeneration(self, failed_hosts, timestamp, db):
        for info_equipo in failed_hosts:
            for nombre_equipo in info_equipo.keys():        
                logger.info("inicia :: obtener info equipos fallidos NextGen")        
                pooles = UtilidadesGrafinitum.obtener_pooles_configurados(self, db, nombre_equipo)
                logger.info("termina :: obtener info equipos fallidos NextGen")        
                for pool in pooles:
                    registro = { 
                        "timestamp":timestamp, 
                        "device":nombre_equipo, 
                        "data":ConstantesGrafinitum.POOLES_NULOS[pool] 
                    }
                    logger.warning(f"REGISTRO DB:: {pool} ::: {registro}")
                    db.saveData(registro, pool)
    
    def construir_informacio_equipos_fallidos_legacy(self, failed_hosts, timestamp, db):
        for info_equipo in failed_hosts:
            for nombre_equipo in info_equipo.keys():                
                pool = "ipv4"
                registro = { 
                    "timestamp":timestamp, 
                    "device":nombre_equipo, 
                    "data":ConstantesGrafinitum.POOLES_NULOS[pool] 
                }
                logger.warning(f"REGISTRO DB:: {pool} ::: {registro}")
                db.saveData(registro, pool) 