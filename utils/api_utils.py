import requests


def getData(apiUrl: str, endpoint: str, dataField: str = None, params: dict = None, headers: dict = None) -> dict:
    """
        Realiza la llamada a la API y retorna los datos en tipo dict

        Args:
            apiUrl (str): URL de la API
            endpoint (str): Endpoint de la API
            dataField (str): Campo de la respuesta que se quiere obtener (opcional)
            params (dict): Parámetros de la petición (opcional)
            headers (dict): Encabezados de la petición (opcional)
        Retorna:
            dict: Diccionario con los datos de la respuesta de la API
    """
    try:
        apiResponse: dict = requests.get(
            f"{apiUrl}/{endpoint}", params=params, headers=headers
        )
        apiResponse.raise_for_status()

        try:
            data = apiResponse.json()
            # Si el usuario no especifica ningún campo, devuelve todo el contenido de la respuesta
            data = data[dataField] if dataField else data
        except:
            print("El formato de la respuesta no es el esperado")
            return None

        return data

    except requests.exceptions.RequestException as e:
        print(f"La petición ha fallado. Código de error: {e}.")
        return None
