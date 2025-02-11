from utils.transforms import *
from utils.storing_utils import saveDataAsDelta
from datetime import datetime
import pandas as pd

bronzeDirectory = "datalake/incremental/bronze"
silverDirectory = "datalake/incremental/silver"
goldDirectory = "datalake/incremental/gold"


def incrementalTransformation(cityName: str) -> pd.DataFrame:
    """
    Esta función se encarga de realizar todo el proceso de transformación incremental, llamando a todas las funciones necesarias.
    Recibe el nombre de la ciudad y la fecha a consultar.

    Args:
    cityName (str): Nombre de la ciudad.

    Retorna:
    pd.DataFrame: DataFrame con la información del clima de la ciudad solicitada procesada.
    """
    # 1. Debemos obtener el data frame de la fecha solicitada y filtrar los resultados por city == cityName
    parsedCityName: str = cityName.strip().lower().replace(" ", "_")
    today = datetime.now().strftime("%Y-%m-%d")
    bronzeDateDirectory = f"""{
        bronzeDirectory}/{parsedCityName}/last_updated_date={today}"""
    bronzeDf = pd.read_parquet(bronzeDateDirectory)

    # 2. Ahora aplicaremos todas las transformaciones silver
    # Eliminamos los nulos
    silverDf = deleteNulls(bronzeDf, ["city", "last_updated_epoch"])
    # Eliminamos los duplicados
    silverDf = deleteDuplicates(silverDf, "last_updated_epoch", [
                                "city"])
    # Formateamos la fecha de epoch al formato habitual argentino DD/MM/AAAA H:M
    silverDf = formatDates(silverDf, "last_updated_epoch", '%d/%m/%Y %H:%M')

    # 3. Guardamos en la capa silver
    silverDateDirectory = f"""{
        silverDirectory}/{parsedCityName}/last_updated_date={today}"""
    saveDataAsDelta(silverDf, silverDateDirectory)

    # 4.Ahora aplicaremos todas las transformaciones gold
    # Mantenemos las columnas deseadas y eliminamos la irrelevantes
    columnsToKeep: list = ["city", "last_updated", "temp_c", "condition",
                           "wind_kph", "humidity"]
    goldDf = deleteColumns(silverDf, columnsToKeep).copy()
    # Definimos los tipos de las columnas remanentes
    columnTypes: dict = {
        "city": "string",
        # ⬇ Hasta ahora se llama last_updated por lo que debería ser un int64 por el epoch, pero ya fue formateado a string previamente
        "last_updated": "string",
        "temp_c": "float32",
        "condition": "string",
        "wind_kph": "int16",
        "humidity": "int8",
    }
    goldDf = defineColumnsTypes(goldDf, columnTypes)
    # Renombramos las columnas remanentes
    newColumnsNames: dict = {
        "city": "ciudad",
        "last_updated": "última_actualización",
        "temp_c": "temperatura (C)",
        "condition": "condición",
        "wind_kph": "velocidad_del_viento (km/h)",
        "humidity": "humedad (%)",
    }
    goldDf = renameColumns(goldDf, newColumnsNames)
    # Agregamos dos columnas

    def highTemp(row) -> pd.DataFrame:
        return row["temperatura (C)"] > 30

    def lowTemp(row) -> pd.DataFrame:
        return row["temperatura (C)"] < 10
    goldDf = addColumn(goldDf, "alerta_calor", bool, highTemp)
    goldDf = addColumn(goldDf, "alerta_frio", bool, lowTemp)

    # 5. Guardamos en la capa gold
    goldDateDirectory = f"{goldDirectory}/{parsedCityName}/date={today}"
    saveDataAsDelta(goldDf, goldDateDirectory)
    return goldDf
