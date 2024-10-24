	# -*- coding: utf-8 -*-
__author__ = 'Abraham Gonzalez Morales, Jesus Barranco Castillo'
__copyright__ = 'Copyright 2021 UNINET. Todos los derechos Reservados'
__version__ = '1.0.0.R1'
__email__ = 'gmoralea@uninet.com.mx, jbarranc@uninet.com.mx'
__status__ = 'Desarrolllo'

import sys
import html
import dominate
# Importar módulos personalizados
from ConstantesPooles import *
from loggingConfig import LoggerFileConfig
from constantesPlugins import LOG_CONFIG_FILES
from modelsPlugins import PluginMail
from utilidadesPlugins import utilidadesPlugins
from dominate.tags import *
from datetime import datetime

# Añadir rutas al sistema
sys.path.append("/home/ngsop/lilaApp/plugins/utilidadesPlugins")
sys.path.append("/home/ngsop/lilaApp/core")

# Configuración del logger
logger = LoggerFileConfig().crearLogFile(LOG_CONFIG_FILES.get("grafinitum"))

class UtilidadesGrafinitum:
    """Utilidades para Grafinitum"""

    def gen_html_alert(self, exception):
        """Genera una alerta en formato HTML."""
        logger.info("inicio::genHTMLAlert:GRAFINITUM")
        try:
            format = datetime.today().strftime('%Y-%m-%d %H:%M')
            doc = dominate.document(title='GRAFINITUM')

            # Leer el archivo CSS
            with open("/home/ngsop/lilaApp/plugins/scripts/monTelcel/style.css") as cssFile:
                cssInfo = cssFile.read()

            # Construir el documento HTML
            with doc.head:
                style(cssInfo)
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
        """Envía una notificación por correo con el mensaje especificado."""
        
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
