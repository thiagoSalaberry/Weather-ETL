from configparser import ConfigParser
from utils.api_utils import getData
from utils.utils import isDateInRange, verifyDate, addDate, verifyCity, addCity
from utils.state_utils import readStateFromJson
from utils.storing_utils import buildTable, readDataFromDelta, saveDataAsDelta
import pandas as pd

parser = ConfigParser()
parser.read("pipeline.conf")
weatherApiData = parser["weather-api"]
API_URL: str = weatherApiData["API_URL"]
endpoint: str = weatherApiData["fullEndpoint"]
key: str = weatherApiData["key"]

headers: dict = {
    "accept": "application/json",
    "key": key
}

baseDir: str = "datalake"
fullBronzeDir: str = f"{baseDir}/full/bronze"
fullGoldDir: str = f"{baseDir}/full/gold"


def fullExtraction(cityName: str, requestedDate: str) -> pd.DataFrame | None:
    """
    Esta función se encarga de realizar todo el proceso de extracción full, llamando a todas las funciones necesarias.
    Llama a la API, guarda los datos en forma cruda y devuelve un data frame.

    Args:
    cityName (str): Nombre de la ciudad.
    requestedDate (str): Fecha de la que se quiere obtener el clima.

    Retorna:
    pd.DataFrame: DataFrame con la información del clima de la ciudad solicitada.
    """
    # 1. Primero validamos que la fecha solicitada se encuentre en el rango esperado
    if not isDateInRange(requestedDate):
        print(f"""❌ La fecha {
              requestedDate} no se encuentra en el rango esperado de 14 a 300 días respecto de hoy.""")
        return None

    # 2. Verificamos en nuestra metadata si la ciudad ya había sido consultada. En tal caso, verificamos si la fecha ya había sido
    # consultada. En tal caso, cortamos el proceso y devolvemos los datos ya almacenados como un data frame. Si no, llamamos a la API
    # para obtener los datos de la nueva fecha.
    # Si la ciudad no existía en nuestra metadata, corremos el procesos desde el comienzo.
    metadataFile: str = "metadata/metadata.json"
    currentMetadata: dict = readStateFromJson(metadataFile)
    parsedCityName: str = cityName.strip().lower().replace(" ", "_")

    # 3. Verificamos si la ciudad solicitada ya había sido consultada previamente
    city: dict | None = verifyCity(currentMetadata, "full", parsedCityName)
    if city:
        # Si la ciudad existe, verifico si la fecha ya había sido consultada
        date: str | None = verifyDate(currentMetadata, "full",
                                      parsedCityName, requestedDate)
        if date:
            # Ya había datos para la fecha solicitada, por lo que debemos devolverlos
            print(f"""💾 La fecha 📅 {
                  requestedDate} ya había sido consultada para la ciudad 🌆 {cityName.title()}""")

            fullGoldDir = f"{baseDir}/full/gold"
            existingData = readDataFromDelta(
                f"{fullGoldDir}/date={requestedDate}")
            if existingData is not None:
                return existingData, 200

    # 4. En este punto, o la ciudad o la fecha no habían sido solicitadas, por lo que corresponde llamar a la API para obtener los últimos resultados
    apiResponse = getData(apiUrl=API_URL, endpoint=endpoint, dataField="forecast", params={
                          "q": cityName, "dt": requestedDate}, headers=headers)

    # 5. Elijo los datos que quiero de la respuesta para poder hacer el data frame
    forecastCleanData = {
        "city": cityName,
        "date": apiResponse["forecastday"][0]["date"],
        "date_epoch": apiResponse["forecastday"][0]["date_epoch"],
        "maxtemp_c": apiResponse["forecastday"][0]["day"]["maxtemp_c"],
        "maxtemp_f": apiResponse["forecastday"][0]["day"]["maxtemp_f"],
        "mintemp_c": apiResponse["forecastday"][0]["day"]["mintemp_c"],
        "mintemp_f": apiResponse["forecastday"][0]["day"]["mintemp_f"],
        "avgtemp_c": apiResponse["forecastday"][0]["day"]["avgtemp_c"],
        "avgtemp_f": apiResponse["forecastday"][0]["day"]["avgtemp_f"],
        "maxwind_mph": apiResponse["forecastday"][0]["day"]["maxwind_mph"],
        "maxwind_kph": apiResponse["forecastday"][0]["day"]["maxwind_kph"],
        "totalprecip_mm": apiResponse["forecastday"][0]["day"]["totalprecip_mm"],
        "totalprecip_in": apiResponse["forecastday"][0]["day"]["totalprecip_in"],
        "avgvis_km": apiResponse["forecastday"][0]["day"]["avgvis_km"],
        "avgvis_miles": apiResponse["forecastday"][0]["day"]["avgvis_miles"],
        "avghumidity": apiResponse["forecastday"][0]["day"]["avghumidity"],
        "condition": apiResponse["forecastday"][0]["day"]["condition"]["text"],
        "uv": apiResponse["forecastday"][0]["day"]["uv"],
        "sunrise": apiResponse["forecastday"][0]["astro"]["sunrise"],
        "sunset": apiResponse["forecastday"][0]["astro"]["sunset"],
        "moonrise": apiResponse["forecastday"][0]["astro"]["moonrise"],
        "moonset": apiResponse["forecastday"][0]["astro"]["moonset"],
        "moon_phase": apiResponse["forecastday"][0]["astro"]["moon_phase"],
        "moon_illumination": apiResponse["forecastday"][0]["astro"]["moon_illumination"]
    }
    forecastDataFrame = buildTable(forecastCleanData)

    # 6. Defino la ruta en la que guardar el delta table y las columnas por las cuales particionar
    partitionCols = "date"

    # 7. Guardo el delta table
    saveDataAsDelta(forecastDataFrame, fullBronzeDir,
                    mode="overwrite", partitionCols=partitionCols)

    # 8. Si todo salió bien, actualizamos nuestro metadata
    if city:
        addDate(currentMetadata, city, requestedDate)
    else:
        newCity = {
            "name": parsedCityName,
            "requestedDates": [requestedDate]
        }
        addCity(currentMetadata, "full", newCity)

    print(f"""✅ Datos nuevos guardados para 🌆 {
          cityName.title()} de la fecha 📅 {requestedDate}""")

    return forecastDataFrame, 201
