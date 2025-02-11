from extraction.full import fullExtraction
from extraction.incremental import incrementalExtraction
from transformation.full import fullTransformation
from transformation.incremental import incrementalTransformation


def main() -> None:
    print(f"""
Trabajo Integrador Ingeniería de Datos 2024 - Thiago Salaberry

Entrega Final

Elegí la extracción a realizar:
1. Extracción Full.
2. Extracción Incremental
""")
    # Solicitar al usuario la opción de extracción
    option: str = input("Ingresá el número de la opción elegida: ").strip()

    if option == "1":
        # Realizar la Extracción Full
        cityName: str = input(
            "Elegí la ciudad a consultar el clima: ").strip().lower()
        date: str = input(
            "Elegí la fecha de la cual querés saber el pronóstico extendido dentro de los próximos 14 a 300 días (formato AAAA-MM-DD): ").strip()
        # Resultado
        resultDf, status = fullExtraction(cityName, date)
        # Si el status es 200, la ciudad ya había sido consultada y transformada a gold, por lo tanto no hace falta volver a transformar
        if resultDf is not None and status == 200:
            print(f"""🌤 Pronóstico extendido para {
                cityName.title()} para el día {date}:""")
            cityGoldDf = resultDf[resultDf["ciudad"] == cityName]
            print(cityGoldDf)
        # Si el status es 201, la ciudad no había sido consultada y por lo tanto hay que transformarla a gold
        if resultDf is not None and status == 201:
            print(f"""🌤 Pronóstico extendido para {
                cityName.title()} para el día {date}:""")
            resultDf = fullTransformation(
                cityName, date, bronzeDataFrame=resultDf)
            print(resultDf)

    elif option == "2":
        # Realizar la Extracción Incremental
        cityName: str = input(
            "Elegí la ciudad de la cual querés consultar el clima actual: ").strip().lower()
        # Resultado
        resultDf = incrementalExtraction(cityName)
        if resultDf is not None:
            print(f"🌤 Clima actual para {cityName.title()}:")
            resultDf = incrementalTransformation(cityName)
            print(resultDf)

    else:
        print("Opción no válida. Por favor, elegí una opción válida (1 ó 2).")


if __name__ == "__main__":
    main()
