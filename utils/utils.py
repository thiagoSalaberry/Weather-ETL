from datetime import datetime, timedelta
from utils.state_utils import writeStateToJson


def isDateInRange(date: str) -> bool:
    """
    Esta función chequea si la fecha solicitada se encuentra dentro de los próximos 14 a 300 días respecto de la fecha de ejecución

    Args:
    date (str): La fecha a verificar en formato 'YYYY-MM-DD'

    Retorna:
    bool: True si la fecha se encuentra dentro del rango, False en caso contrario
    """

    # Primero, obtenemos la fecha actual
    today = datetime.now()

    # Luego, convertimos la fecha ingresada a un objeto datetime
    date = datetime.strptime(date, '%Y-%m-%d')

    # Calculamos la fecha límite inferior (14 días después de la fecha actual)
    lower_limit = today + timedelta(days=14)

    # Calculamos la fecha límite superior (300 días después de la fecha actual)
    upper_limit = today + timedelta(days=300)

    # Verificamos si la fecha ingresada se encuentra dentro del rango
    return lower_limit <= date <= upper_limit


def verifyCity(currentMetadata: dict, section: str, cityName: str) -> dict | None:
    """
    Esta función verifica si una ciudad ya ha sido solicitada por el usuario

    Args:
    currentMetadata (dict): El objeto que contiene la información de la ciudad solicitada por el usuario
    section (str): La sección del objeto currentMetadata (full o incremental)
    cityName (str): El nombre de la ciudad a verificar

    Retorna:
    dict | None: El estado de la ciudad si ya ha sido solicitada, None en caso de que no
    """
    # 1. Buscamos la ciudad en la list de ciudades
    cities = currentMetadata[section]["cities"]
    city = next((city for city in cities
                if city["name"] == cityName), None)
    return city


def addCity(currentMetadata: dict, section: str, newCity: dict) -> None:
    """
    Esta función se encarga de agregar la ciudad con la primera fecha consultada al archivo metadata.json

    Args:
    currentMetadata (dict): El estado actual del archivo
    section (str): La sección del objeto currentMetadata (full o incremental)
    newCity (dict): La ciudad a agregar con su nombre y fecha

    Retorna:
    None
    """
    currentCities: list = currentMetadata[section]["cities"]
    currentCities.append(newCity)
    writeStateToJson("metadata/metadata.json", currentMetadata)


def verifyDate(currentMetadata: dict, section: str, cityName: str, requestedDate: str) -> str | None:
    """
    Para extracción full.
    Esta función chequea si la fecha para la ciudad ya había sido solicitada. En tal caso, devuelve los datos almacenados;
    en caso contrario, devuelve False y permite que el programa continúe.

    Args:
    currentMetadata (dict): El estado actual del archivo
    section (str): La sección del objeto currentMetadata (full o incremental)
    cityName (str): El nombre de la ciudad a verificar
    requestedDate (str): La fecha solicitada por el usuario

    Retorna:
    str | None: La fecha si ya ha sido solicitada, None en caso de que no
    """
    # 1. Buscamos la fecha en la lista de fechas consultadas
    city = verifyCity(currentMetadata, section, cityName)
    date = next(
        (date for date in city["requestedDates"] if date == requestedDate), None)
    return date


def addDate(currentMetadata: dict, city: dict, requestedDate: str) -> None:
    """
    Esta función se encarga de agregar requestedDate a las fechas consultadas y guardarlo en metadata.json

    Args:
    currentMetadata (dict): El estado actual del archivo
    city (dict): Los datos de la ciudad (name:str, requestedDates:str[])
    requestedDate (str): La fecha solicitada para la ciudad

    Retorna:
    None
    """
    city["requestedDates"].append(requestedDate)
    writeStateToJson("metadata/metadata.json", currentMetadata)


def updateLastUpdated(currentMetadata: dict, city: dict) -> None:
    """
    Esta función se encarga de actualizar el último momento de ejecución en el proceso incremental para una ciudad en metadata.json

    Args:
    currentMetadata (dict): El estado actual del archivo
    cityName (str): El nombre de la ciudad a actualizar

    Retorna:
    None
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    city["lastUpdated"] = now
    writeStateToJson("metadata/metadata.json", currentMetadata)
