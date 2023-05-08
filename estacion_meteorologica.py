import requests
from io import StringIO
import json
import datetime
import pandas as pd


class EstacionMeteorologica:
    """
    Clase para extraer y procesar datos meteorológicos de una estación específica.
    """

    def __init__(self, api_key, station_id):
        """
        Inicializa la clase EstacionMeteorologica con la API_KEY y el STATION_ID.

        :param api_key: str, clave de API para acceder a los datos meteorológicos.
        :param station_id: str, identificador de la estación meteorológica.
        """
        self.api_key = api_key
        self.station_id = station_id
        self.datos = pd.DataFrame()

    def obtener_datos_estacion(self, fecha_inicio):
        """
        Obtiene los datos meteorológicos de la estación desde la fecha de inicio hasta la fecha actual.

        :param fecha_inicio: datetime.date, fecha de inicio para obtener los datos.
        """
        fecha_actual = datetime.datetime.now().date()

        while fecha_inicio < fecha_actual:
            url = f"https://api.weather.com/v2/pws/history/daily?stationId={self.station_id}&format=json&units=m&numericPrecision=decimal&date={fecha_inicio.strftime('%Y%m%d')}&apiKey={self.api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = StringIO(response.text)
                json_data = data.read()
                df_temp = pd.json_normalize(json.loads(json_data), record_path='observations')
                self.datos = pd.concat([self.datos, df_temp])
            else:
                print(f"Error al obtener datos: {response.status_code}")
            fecha_inicio += datetime.timedelta(days=1)

    def limpieza_datos(self):
        """
        Limpia los datos eliminando filas duplicadas y valores anómalos.
        """
        self.datos = self.datos.drop_duplicates()

        # Reemplaza los límites según tus necesidades
        self.datos = self.datos[(self.datos['metric.tempAvg'] >= -50) & (self.datos['metric.tempAvg'] <= 50)]
        self.datos = self.datos[(self.datos['humidityAvg'] >= 0) & (self.datos['humidityAvg'] <= 100)]

    def get_datos(self):
        """
        Retorna el DataFrame con los datos meteorológicos extraídos y procesados.

        :return: pd.DataFrame, DataFrame con los datos meteorológicos.
        """
        return self.datos

