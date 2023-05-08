import pandas as pd


class AnalizadorMeteorologico:
    """
    Clase para analizar datos meteorológicos y calcular resúmenes entre dos fechas.
    """

    def __init__(self, datos_meteorologicos):
        """
        Inicializa la clase AnalizadorMeteorologico con el DataFrame de datos meteorológicos.

        :param datos_meteorologicos: pd.DataFrame, DataFrame con los datos meteorológicos.
        """
        self.datos = datos_meteorologicos

    def calcular_resumen(self, fecha_inicio, fecha_final, frecuencia='D'):
        """
        Calcula el resumen (media) de los datos meteorológicos entre dos fechas con una frecuencia específica.

        :param fecha_inicio: str, fecha de inicio en formato 'YYYY-MM-DD'.
        :param fecha_final: str, fecha final en formato 'YYYY-MM-DD'.
        :param frecuencia: str, frecuencia para calcular el resumen ('D' para días, 'W' para semanas, 'M' para meses).
        :return: pd.DataFrame, DataFrame con el resumen de los datos meteorológicos.
        """
        if frecuencia not in ['D', 'W', 'M']:
            raise ValueError("La frecuencia debe ser 'D' (días), 'W' (semanas) o 'M' (meses)")

        # Filtrar datos entre las fechas proporcionadas
        self.datos['datetime'] = pd.to_datetime(self.datos['obsTimeUtc'])
        datos_filtrados = self.datos[(self.datos['datetime'] >= fecha_inicio) & (self.datos['datetime'] <= fecha_final)]

        # Calcular el resumen (media) de los datos agrupados por frecuencia
        if frecuencia == 'D':
            resumen = datos_filtrados.resample('D', on='datetime').mean().dropna()
        elif frecuencia == 'W':
            resumen = datos_filtrados.resample('W', on='datetime').mean().dropna()
        else:  # 'M'
            resumen = datos_filtrados.resample('M', on='datetime').mean().dropna()

        return resumen

    def get_columns(self, columnas):
        """
        Filtra las columnas deseadas del DataFrame de datos meteorológicos.

        :param columnas: list, columnas para incluir en el DataFrame resultante.
        :return: pd.DataFrame, DataFrame con las columnas deseadas.
        """
        return self.datos[columnas]
