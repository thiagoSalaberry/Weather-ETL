import pandas as pd


def deleteNulls(df: pd.DataFrame, columnsSubset: list) -> pd.DataFrame:
    """
    Esta función se encargará de eliminar los registros en los que las columnas pasadas sean null

    Args:
    df (pd.DataFrame): Data frame a tratar

    Retorna:
    pd.DataFrame: Data frame sin registros con null en las columnas pasadas
    """
    df = df.dropna(subset=columnsSubset)
    return df


def deleteDuplicates(df: pd.DataFrame, sortByAscending: str, columnsSubset: list) -> pd.DataFrame:
    """
    Esta función se encargará de eliminar los registros duplicados en el data frame en las columnas pasadas y se quedará con el último
    en base a la columna pasada    

    Args:
    df (pd.DataFrame): Data frame a tratar
    sortByAscending (str): Columna en base a la cual se ordenarán los registros para mantener el último
    columnsSubset (list): Columnas en base a las cuales se compararán los registros

    Retorna:
    pd.DataFrame: Data frame sin registros duplicados en las columnas pasadas
    """
    df = df.sort_values(sortByAscending, ascending=True).drop_duplicates(
        subset=columnsSubset, keep="last")
    return df


def formatDates(df: pd.DataFrame, dateColumn: str, desiredFormat: str) -> pd.DataFrame:
    """
    Esta función se encargará de formatear las fechas para dejarlas en el formato deseado

    Args:
    df (pd.DataFrame): Data frame a tratar
    dateColumn (str): Columna que contiene las fechas a formatear
    desiredFormat (str): Formato deseado para las fechas

    Retorna:
    pd.DataFrame: Data frame con las fechas formateadas
    """
    df[dateColumn] = pd.to_datetime(
        df[dateColumn], unit="s").dt.strftime(desiredFormat)
    return df


def addColumn(df: pd.DataFrame, columnName: str, dtype: type, logic: callable) -> pd.DataFrame:
    """
    Esta función se encargará de agregar una columna al Data frame con un valor definido por lógica personalizada.

    Args:
    df (pd.DataFrame): Data frame a tratar
    columnName (str): Nombre de la columna a agregar
    dtype (type): Tipo de dato de la columna a agregar
    logic (callable): Lógica para calcular el valor de la columna a agregar

    Retorna:
    pd.DataFrame: Data frame con la columna agregada
    """
    df[columnName] = df.apply(logic, axis=1).astype(dtype)
    return df


def deleteColumns(df: pd.DataFrame, columnsToKeep: list) -> pd.DataFrame:
    """
    Esta función se encargará de mantener las columnas especificadas, eliminando las restantes

    Args:
    df (pd.DataFrame): Data frame a tratar
    columnsToKeep (list): lista de columnas a mantener

    Retorna:
    pd.DataFrame: Data frame sin las columnas eliminadas
    """
    df = df[columnsToKeep]
    return df


def defineColumnsTypes(df: pd.DataFrame, columnTypes: dict) -> pd.DataFrame:
    """
    Asigna tipos de datos específicos a las columnas del data frame

    Args:
    df (pd.DataFrame): Data frame a tratar
    columnTypes (dict): Diccionario con columnas como claves y tipos de datos como valores

    Retorna:
    pd.DataFrame: Data frame con los tipos de datos asignados
    """
    for column, columnType in columnTypes.items():
        if column in df.columns:
            try:
                df[column] = df[column].astype(columnType)
            except Exception as e:
                print(f"""Error al convertir la columna '{
                      column}' a '{columnType}': {e}""")
    return df


def renameColumns(df: pd.DataFrame, newColumnsNames: dict) -> pd.DataFrame:
    """
    Esta función se encargará de renombrar y traducir las columnas al español

    Args:
    df (pd.DataFrame): Data frame a tratar
    newColumnsNames (dict): Diccionario donde las claves son los nombres actuales y los valores son los nombres nuevos

    Retorna:
    pd.DataFrame: Data frame con las columnas renombradas y traducidas
    """
    df = df.rename(columns=newColumnsNames)
    return df
