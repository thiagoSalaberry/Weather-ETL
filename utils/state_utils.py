import json


def readStateFromJson(filePath: str) -> dict:
    """
    Lee el archivo JSON que contiene los metadatos

    Args:
    filePath (str): Ruta del archivo JSON que contiene los metadatos.

    Retorna:
    dict: Diccionario con los metadatos.
    """
    try:
        with open(filePath, "r") as file:
            state = json.load(file)
            return state
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"""❌ El archivo JSON en la ruta {
                                   filePath} no es válido.""")


def updateJsonData(currentData: dict[str, any], newData: dict[str, any]) -> dict[str, any]:
    """
    Actualiza los datos actuales con los nuevos datos.

    Args:
    currentData (dict[str, any]): Diccionario con los datos actuales.
    newData (dict[str, any]): Diccionario con los nuevos datos.

    Retorna:
    dict[str, any]: Diccionario con los datos actualizados.
    """
    updatedData = currentData.copy()

    for key, value in newData.items():
        if key in updatedData and isinstance(updatedData[key], dict) and isinstance(value, dict):
            for subKey, subValue in value.items():
                if isinstance(updatedData[key].get(subKey), key) and isinstance(subValue, list):
                    updatedData[key][subKey] = list(
                        set(updatedData[key][subKey] + subValue))
                else:
                    updatedData[key] = value

    return updatedData


def writeStateToJson(filePath: str, state: dict) -> None:
    """
    Sobreescribe el archivo JSON con la última fecha de ejecución.

    Parámetros:
    filePath (str): Ruta del archivo JSON que contiene los metadatos.
    state (dict): Diccionario con los metadatos.

    Retorna:
    None
    """
    try:
        with open(filePath, "w") as file:
            json.dump(state, file, default=str, indent=4)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"❌ El archivo JSON no existe en la ruta {filePath}.")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"""❌ El archivo JSON en la ruta {
                                   filePath} no es válido.""")
