from utils.transforms import *
from utils.storing_utils import saveDataAsDelta
import pandas as pd

bronzeDirectory = "datalake/full/bronze"
silverDirectory = "datalake/full/silver"
goldDirectory = "datalake/full/gold"


def fullTransformation(cityName: str, requestedDate: str, bronzeDataFrame: pd.DataFrame) -> pd.DataFrame:
    """
    Esta función se encarga de realizar todo el proceso de transformación full, llamando a todas las funciones necesarias.
    Recibe el nombre de la ciudad y la fecha a consultar.

    Args:
    cityName (str): Nombre de la ciudad.
    requestedDate (str): Fecha de la que se quiere obtener el clima procesado.

    Retorna:
    pd.DataFrame: DataFrame con la información del clima de la ciudad solicitada.
    """
    # 1. Recibo el data frame bronce de la extracción que incluye todas las ciudades, por lo tanto debo elegir solo la requerida
    bronzeCityDf = bronzeDataFrame[bronzeDataFrame["city"] == cityName].copy(
    )
    # 2. Ahora aplicaremos todas las transformaciones silver
    # Eliminamos los nulos
    silverDf = deleteNulls(bronzeCityDf, ["city", "date_epoch"])
    # Eliminamos los duplicados
    silverDf = deleteDuplicates(silverDf, "date_epoch", [
                                "city", "date_epoch"])
    # Formateamos la fecha de epoch al formato habitual argentino DD/MM/AAAA
    silverDf = formatDates(silverDf, "date_epoch", '%d/%m/%Y')

    # 3. Guardamos en la capa silver
    silverDateDirectory = f"{silverDirectory}/date={requestedDate}"
    saveDataAsDelta(silverDf, silverDateDirectory)

    # 4.Ahora aplicaremos todas las transformaciones gold
    # Mantenemos las columnas deseadas y eliminamos la irrelevantes
    columnsToKeep: list = ["city", "date_epoch", "avgtemp_c", "maxtemp_c", "mintemp_c",
                           "condition", "maxwind_kph", "avghumidity", "sunrise", "sunset", "moonrise", "moon_phase"]
    goldDf = deleteColumns(silverDf, columnsToKeep).copy()
    # Definimos los tipos de las columnas remanentes
    columnTypes: dict = {
        "city": "string",
        # ⬇ Hasta ahora se llama date_epoch por lo que debería ser un int64, pero ya fue formateado a string previamente
        "date_epoch": "string",
        "avgtemp_c": "float32",
        "maxtemp_c": "float32",
        "mintemp_c": "float32",
        "condition": "string",
        "maxwind_kph": "int16",
        "avghumidity": "int8",
        "sunrise": "string",
        "sunset": "string",
        "moonrise": "string",
        "moon_phase": "string",
    }
    goldDf = defineColumnsTypes(goldDf, columnTypes)
    # Renombramos las columnas remanentes
    newColumnsNames: dict = {
        "city": "ciudad",
        "date_epoch": "fecha",
        "avgtemp_c": "temp_promedio (C)",
        "maxtemp_c": "temp_máxima (C)",
        "mintemp_c": "temp_mínima (C)",
        "condition": "condición",
        "maxwind_kph": "viento_máximo (km/h)",
        "avghumidity": "humedad_promedio (%)",
        "sunrise": "amanecer",
        "sunset": "atardecer",
        "moonrise": "anochecer",
        "moon_phase": "fase_lunar",
    }
    goldDf = renameColumns(goldDf, newColumnsNames)
    # Agregamos dos columnas

    def highTemp(row) -> pd.DataFrame:
        return row["temp_promedio (C)"] > 30

    def lowTemp(row) -> pd.DataFrame:
        return row["temp_promedio (C)"] < 10
    goldDf = addColumn(goldDf, "alerta_calor", bool, highTemp)
    goldDf = addColumn(goldDf, "alerta_frio", bool, lowTemp)

    # 5. Guardamos en la capa gold
    goldDateDirectory = f"{goldDirectory}/date={requestedDate}"
    saveDataAsDelta(goldDf, goldDateDirectory)
    return goldDf
