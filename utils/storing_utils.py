import pandas as pd
import pyarrow as pa
from deltalake import write_deltalake, DeltaTable
from deltalake.exceptions import TableNotFoundError
import pprint


def readDataFromDelta(path: str) -> pd.DataFrame:
    """
    Lee los datos de una tabla Delta Lake desde una ruta especificada.

    Args:
      path (str): La ruta completa donde se encuentra el archivo Delta.

    Returns:
      pd.DataFrame: El DataFrame con los datos leídos de la tabla Delta.
    """
    try:
        df = pd.read_parquet(path)
        return df
    except Exception as e:
        print(f"""Error al leer el archivo Parquet en la ruta: {
              path}. Detalles del error: {e}""")
        return None


def saveDataAsDelta(dataFrame: pd.DataFrame, path: str, mode: str = "overwrite", partitionCols: list | str = None):
    """
    Guarda un dataframe en formato Delta Lake en la ruta especificada.
    A su vez, es capaz de particionar el dataframe por una o varias columnas.
    Por defecto, el modo de guardado es "overwrite".

    Args:
      df (pd.DataFrame): El dataframe a guardar.
      path (str): La ruta donde se guardará el dataframe en formato Delta Lake.
      mode (str): El modo de guardado. Son los modos que soporta la libreria
      deltalake: "overwrite", "append", "error", "ignore".
      partition_cols (list or str): La/s columna/s por las que se particionará el
      dataframe. Si no se especifica, no se particionará.
    """
    write_deltalake(path, dataFrame, mode=mode, partition_by=partitionCols)


def saveNewDataAsDelta(newData: pd.DataFrame, path: str, predicate: str, partitionCols=None):
    """
    Guarda solo nuevos datos en formato Delta Lake usando la operación MERGE,
    comparando los datos ya cargados con los datos que se desean almacenar
    asegurando que no se guarden registros duplicados.

    Args:
      new_data (pd.DataFrame): Los datos que se desean guardar.
      data_path (str): La ruta donde se guardará el dataframe en formato Delta Lake.
      predicate (str): La condición de predicado para la operación MERGE.
      partition_cols (list or str): La/s columna/s por las que se particionará el
      dataframe. Si no se especifica, no se particionará.
    """
    try:
        dt = DeltaTable(path)
        newDataPa = pa.Table.from_pandas(newData)
        # Se insertan en target datos del source que no existan en el target
        dt.merge(
            source=newDataPa,
            source_alias="source",
            target_alias="target",
            predicate=predicate
        )\
            .when_not_matched_insert_all()\
            .execute()
    except TableNotFoundError:
        saveDataAsDelta(newData, path, mode="overwrite",
                        partitionCols=partitionCols)


def upsertDataAsDelta(data: pd.DataFrame, path: str, predicate: str):
    """
    Guardar datos en formato Delta Lake usando la operacion MERGE.
    Cuando no haya registros coincidentes, se insertarán nuevos registros.
    Cuando haya registros coincidentes, se actualizarán los campos.

    Args:
      data (pd.DataFrame): Los datos que se desean guardar.
      data_path (str): La ruta donde se guardará el dataframe en formato Delta Lake.
      predicate (str): La condición de predicado para la operación MERGE.
    """
    try:
        dt = DeltaTable(path)
        dataPa = pa.Table.from_pandas(data)
        dt.merge(
            source=dataPa,
            source_alias="source",
            target_alias="target",
            predicate=predicate
        )\
            .when_matched_update_all()\
            .when_not_matched_insert_all()\
            .execute()
    except TableNotFoundError:
        saveDataAsDelta(data, path, mode="overwrite")


def buildTable(jsonData: dict) -> pd.DataFrame:
    """
    Esta función se encarga de construir el data frame con los datos en formato JSON.

    Args:
    jsonData (dict): Los datos en formato JSON.

    Retorna:
    pd.DataFrame: El data frame con los datos en formato JSON.
    """

    try:
        dataFrame = pd.json_normalize(jsonData)
        return dataFrame
    except:
        print("Error al construir el data frame. Los datos no están en formato JSON.")
        return None
