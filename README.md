# Agro Weather

Agro Weather is a Python application that collects meteorological data from a given weather station and calculates agricultural parameters such as evapotranspiration (ETc) and water requirements. The data is stored in a SQLite database for further analysis.

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/antoniofcano/agro-wu.git
    ```
2. Install the dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

1. Import the necessary classes:
    ```python
    from bbdd_meteorologica import GestorBBDD, EstacionMeteorologica
    from agro_calculations import AgroCalculations
    ```

2. Create an instance of the `EstacionMeteorologica` class:
    ```python
    estacion = EstacionMeteorologica(api_key, station_id)
    ```

3. Create an instance of the `GestorBBDD` class:
    ```python
    gestor = GestorBBDD(db_name, table_name, estacion, latitude, elevation, growth_stage)
    ```

4. Call the `actualizar_datos` method to update the data in the database:
    ```python
    gestor.actualizar_datos()
    ```

## Notes

- Replace `api_key`, `station_id`, `db_name`, `table_name`, `latitude`, `elevation`, and `growth_stage` with your actual values.
- `latitude` should be in decimal degrees.
- `elevation` should be in meters.
- `growth_stage` should be one of the following: 'initial', 'crop development', 'mid-season', or 'late season'.

## License

