# Curso de Ingeniería de Datos - Año 2024

## Trabajo Final Integrador - Thiago Salaberry

## ▶ HOW TO USE

1.  Clone or download this repo
2.  Create a virtual environment as follows:  
    In your command line:

    # bash

    1️⃣
    python -m venv venv
    source venv/Scripts/activate

    2️⃣
    pip install -r requirements.txt

    3️⃣
    py index.py

## CÓMO USAR

1.  Clonar o descargar repo
2.  Crear un entorno virtual de la siguiente manera:
    En tu línea de comandos

    # bash

    1️⃣
    python -m venv venv
    source venv/Scripts/activate

    2️⃣
    pip install -r requirements.txt

    3️⃣
    py index.py

### Consigna:

#### Parte 1

Desarrollar un programa en Python que:

1. Extraiga datos de una API como fuente de datos.
2. Convierta los datos obtenidos como DataFrames de Pandas
3. Los guarde en forma cruda, sin transformaciones o con leves transformaciones en formato Delta Lake.

## Propuesta

Realizaremos consultas a la API `http://api.weatherapi.com/v1/` para obtener datos meteorológicos, ya que sirven para realizar tanto extracciones full como incrementales.

La **Extracción Full** llamará al endpoint `future.json` con una query `q` que representa a una ciudad y con otra query `dt` que representa la fecha, y nos servirá para realizar consultas sobre el pronóstico extendido de dicha ciudad entre los próximos 14 y 300 días respecto
al día en que se realiza la consulta.

La **Extracción Incremental** llamará al endpoint `current.json` también con una query `q` que representa a una ciudad y nos servirá para
realizar consultas sobre el estado del clima actual en dicha ciudad, ya que es un endpoint que actualiza los datos que devuelve cada 15 minutos.

Los datos de ambas extracciones se guardarán en formato Delta Lake en la carpeta 📁/datalake de la siguiente manera:

📁/datalake
┣━ 📁/incremental
┃...┣━ 📁/bronze
┃...┃...┣━ 📁/ciudad_1
┃...┃...┃...┗━ 📁/ultima_fecha_de_actualizacion
┃...┃...┃......┗━ 📃archivo00:00:00.parquet
┃...┃...┃......┗━ 📃archivo00:00:15.parquet
┃...┃...┣━ 📁/ciudad_2
┃...┃...┗━ 📁/ciudad_3
┃...┣━ 📁/silver
┃...┃...┣━ 📁/ciudad_1
┃...┃...┃...┗━ 📁/ultima_fecha_de_actualizacion
┃...┃...┃......┗━ 📃archivo00:00:00.parquet
┃...┃...┃......┗━ 📃archivo00:00:15.parquet
┃...┃...┣━ 📁/ciudad_2
┃...┃...┗━ 📁/ciudad_3
┃...┗━ 📁/gold
┃.......┣━ 📁/ciudad_1
┃.......┃...┗━ 📁/ultima_fecha_de_actualizacion
┃.......┃......┗━ 📃archivo00:00:00.parquet
┃.......┃......┗━ 📃archivo00:00:15.parquet
┃.......┣━ 📁/ciudad_2
┃.......┗━ 📁/ciudad_3
┃
┗━ 📁/full
....┣━ 📁/bronze
....┃...┣━ 📁/fecha_1
....┃...┃...┗━ 📃ciudad_1.parquet
....┃...┃...┗━ 📃ciudad_2.parquet
....┃...┃...┗━ 📃ciudad_3.parquet
....┃...┣━ 📁/fecha_2
....┃...┗━ 📁/fecha_3
....┣━ 📁/silver
....┃...┣━ 📁/fecha_1
....┃...┃...┗━ 📃ciudad_1.parquet
....┃...┃...┗━ 📃ciudad_2.parquet
....┃...┃...┗━ 📃ciudad_3.parquet
....┃...┣━ 📁/fecha_2
....┃...┗━ 📁/fecha_3
....┗━ 📁/gold
........┣━ 📁/fecha_1
........┃...┗━ 📃ciudad_1.parquet
........┃...┗━ 📃ciudad_2.parquet
........┃...┗━ 📃ciudad_3.parquet
........┣━ 📁/fecha_2
........┗━ 📁/fecha_3

Estas extracciones se realizarán apoyadas en un archivo 📃metadata.json, que contendrá datos sobre las últimas peticiones de las ciudades
requeridas, para saber si tiene que almacenar los últimos datos o ignorarlos ya que no son lo suficientemente nuevos. Tendrá el siguiente
formato:
{
...."incremental": {
........"cities": [
............{
................"name": "ciudad_1",
................"lastUpdated": "AAAA-MM-DD hh:mm:ss"
............},
............{
................"name": "ciudad_2",
................"lastUpdated": "AAAA-MM-DD hh:mm:ss"
............}
........]
....},
...."full": {
........"cities": [
............{
................"name": "ciudad_1",
................"requestedDates": [
...................."fecha_1(AAAA-MM-DD)",
...................."fecha_2(AAAA-MM-DD)",
................]
............},
............{
................"name": "ciudad_2",
................"requestedDates": [
...................."fecha_1(AAAA-MM-DD)",
...................."fecha_1(AAAA-MM-DD)",
................]
............}
........]
....}
}
Las peticiones de la extracción full se realizarán una sola vez, ya que los datos se generan una sola vez para las fechas entre los 14 y 300 próximos días y no se actualizan, por lo que no vale la pena realizar el proceso más de una ves.
Si se quieren realizar consultas para fechas dentro de los próximos 14 días, se debe recurrir a otro endpoint lo cual no está visto en este trabajo.

#### Parte 2

Leer los datos almacenados en la parte 1 y aplicar tareas de procesamiento o transformaciones de datos con Pandas. Esas tareas pueden ser:

- Eliminación de duplicados
- Eliminación o reemplazo de nulos
- Conversión de tipos de datos de columnas
- Renombrar columnas
- Formatear columnas de tipo fecha.
- Crear nuevas columnas a partir de alguna lógica (Por ejemplo, una columna
  booleana que indique si una temperatura está por arriba de un límite)
- Cruzar dataframes usando JOINS
- Aplicar agregaciones por medio de GROUP BY y funciones como MAX, MIN,
  AVG, etc.
- etc.

Se deberán realizar al menos 4 tareas de transformación.

El resultado del procesamiento debe ser guardado en uno, o varios, archivos Delta lake en el directorio que corresponda.

#### Propuesta

Realizaremos las siguiente transformaciones:

1. Trataremos los registros con posibles valores nulos:
   A. Data Frame de extracción full: columnas `city` y `date_epoch`
   B. Data Frame de extracción incremental: columnas `city` y `last_updated_epoch`
2. Eliminaremos los duplicados de las ciudades en las que haya más de un registro:
   A. Data Frame de extracción full: columnas `city` y `date_epoch`
   B. Data Frame de extracción incremental: columnas `city` y se quedará con el último registro ordenando por `last_updated_epoch`
3. Formatearemos las fechas para que se vean en el formato habitual argentino de DD/MM/AAAA agregando la fecha para la extracción incremental
4. Eliminaremos columnas irrelevantes
5. Definiremos los tipos de las columnas remanentes
6. Renombraremos las columnas remanentes
7. Crearemos una columna nueva de alerta de calor cuando una temperatura supere los 30°C y una nueva columna alerta de frío cuando la temperatura sea inferior a los 10°C
8. Realizaremos joins entre las tablas del clima actual y del pronóstico del mismo día para cierta ciudad para calcular diferencias de cierto valores

## Conclusión

Crearemos un programa en Python que haga llamadas a una API de clima para consultar el estado actual del clima y el pronóstico de cierta fecha de un lugar elegido.

Las respuestas que obtengamos las guardaremos en una capa 'bronze' para su posterior procesamiento.
El procesamiento consistirá en transformaciones típicas como eliminación de duplicados y tratamiento de nulos, entre otros, que se guardarán en la capa 'silver', y transformaciones orientadas a la lógica del negocio que se guardarán en la capa 'gold'. Estas últimas serán eliminar columnas intracendentes, renombrar las remanentes, agregar una columna de 'alerta de calor' y de 'alerta de frío' con un valor booleano en caso de que se cumpla una condición dada.
