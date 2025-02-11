from configparser import ConfigParser
from utils.api_utils import getData
from utils.utils import verifyCity, addCity, updateLastUpdated
from utils.state_utils import readStateFromJson
from utils.storing_utils import buildTable, readDataFromDelta, saveDataAsDelta
from datetime import datetime
import pandas as pd

parser = ConfigParser()
parser.read("pipeline.conf")
weatherApiData = parser["weather-api"]
API_URL: str = weatherApiData["API_URL"]
endpoint: str = weatherApiData["incrementalEndpoint"]
key: str = weatherApiData["key"]

headers: dict = {
    "accept": "application/json",
    "key": key
}

baseDir: str = "datalake"
incrementalBronzeDir: str = f"{baseDir}/incremental/bronze"


def incrementalExtraction(cityName: str) -> pd.DataFrame | None:
    """
    Esta función se encarga de realizar todo el proceso de extracción incremental, llamando a todas las funciones necesarias.
    Llama a la API, guarda los datos en forma cruda y devuelve un data frame.

    Args:
    cityName (str): Nombre de la ciudad.

    Retorna:
    pd.DataFrame: DataFrame con la información del clima actual de la ciudad solicitada.
    """
    # 1. Llamo a la API para obtener los últimos resultados
    apiResponse = getData(apiUrl=API_URL, endpoint=endpoint,
                          dataField="current", params={"q": cityName}, headers=headers)

    # 2. Verifico si la ciudad ya fue solicitada. Si no, se agrega con un valor anómalo para la primera ejecución.
    metadataFile: str = "metadata/metadata.json"
    currentMetadata: dict = readStateFromJson(metadataFile)
    parsedCityName: str = cityName.strip().lower().replace(" ", "_")
    cityDir = f"{incrementalBronzeDir}/{parsedCityName}"
    city = verifyCity(currentMetadata, "incremental", parsedCityName)
    if not city:
        city: dict = {
            "name": parsedCityName,
            "lastUpdated": "1900-01-01"
        }
        addCity(currentMetadata, "incremental", city)

    # 3. Comparamos los últimos momento de ejecución
    lastUpdated = city["lastUpdated"]
    apiLastUpdated = apiResponse["last_updated"]
    # Si la última actualización de la API es previa al último momento de ejecución, devuelvo los datos almacenados previamente
    if apiLastUpdated < lastUpdated:
        cityCurrentWeatherDataFrame = readDataFromDelta(cityDir)
        return cityCurrentWeatherDataFrame

    # 4. Elijo los datos que quiero de la respuesta para poder hacer el data frame
    currentWeatherCleanData = {
        "city": cityName,
        "last_updated_epoch": apiResponse["last_updated_epoch"],
        "last_updated": apiResponse["last_updated"],
        "temp_c": apiResponse["temp_c"],
        "temp_f": apiResponse["temp_f"],
        "is_day": apiResponse["is_day"],
        "condition": apiResponse["condition"]["text"],
        "wind_mph": apiResponse["wind_mph"],
        "wind_kph": apiResponse["wind_kph"],
        "wind_degree": apiResponse["wind_degree"],
        "wind_dir": apiResponse["wind_dir"],
        "pressure_mb": apiResponse["pressure_mb"],
        "pressure_in": apiResponse["pressure_in"],
        "precip_mm": apiResponse["precip_mm"],
        "precip_in": apiResponse["precip_in"],
        "humidity": apiResponse["humidity"],
        "cloud": apiResponse["cloud"],
        "feelslike_c": apiResponse["feelslike_c"],
        "feelslike_f": apiResponse["feelslike_f"],
        "windchill_c": apiResponse["windchill_c"],
        "windchill_f": apiResponse["windchill_f"],
        "heatindex_c": apiResponse["heatindex_c"],
        "heatindex_f": apiResponse["heatindex_f"],
        "dewpoint_c": apiResponse["dewpoint_c"],
        "dewpoint_f": apiResponse["dewpoint_f"],
        "vis_km": apiResponse["vis_km"],
        "vis_miles": apiResponse["vis_miles"],
        "uv": apiResponse["uv"],
        "gust_mph": apiResponse["gust_mph"],
        "gust_kph": apiResponse["gust_kph"]
    }

    # 5. Guardo el delta table
    cityCurrentWeatherDataFrame = buildTable(currentWeatherCleanData)
    # Agrego una columna llamada last_updated_date para que la partición se realice por fecha y no por hora,
    # y en dicha carpeta se almacenen todos los archivos de ciudades para la misma fecha
    cityCurrentWeatherDataFrame["last_updated_date"] = cityCurrentWeatherDataFrame["last_updated"].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d")
    )
    saveDataAsDelta(cityCurrentWeatherDataFrame, cityDir,
                    mode="overwrite", partitionCols="last_updated_date")

    # 6. Actualizo los datos y lastUpdated en metadata
    updateLastUpdated(currentMetadata, city)
    return cityCurrentWeatherDataFrame
