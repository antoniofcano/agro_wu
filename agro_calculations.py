# agro_calculations.py
import math

class AgroCalculations:
    def __init__(self, latitude, elevation, growth_stage):
        self.latitude = latitude
        self.elevation = elevation
        self.growth_stage = growth_stage
        self.irrigation_efficiency = 0.75

    def _solar_declination(self, day_of_year: int) -> float:
        return 0.409 * math.sin(2 * math.pi * (day_of_year + 284) / 365)

    def _relative_sun_earth_distance(self, day_of_year: int) -> float:
        return 1 + 0.033 * math.cos(2 * math.pi * day_of_year / 365)

    def _sunset_hour_angle(self, declination: float) -> float:
        return math.acos(-math.tan(math.radians(self.latitude)) * math.tan(declination))

    def _extraterrestrial_radiation(self, day_of_year: int) -> float:
        declination = self._solar_declination(day_of_year)
        relative_distance = self._relative_sun_earth_distance(day_of_year)
        hour_angle = self._sunset_hour_angle(declination)
        return (24 * 60 * 0.0820) / math.pi * relative_distance * (hour_angle * math.sin(math.radians(self.latitude)) * math.sin(declination) + math.cos(math.radians(self.latitude)) * math.cos(declination) * math.sin(hour_angle))

    def _get_crop_coefficient(self) -> float:
        kc_values = {
            "parada_invernal": 0.4,
            "desarrollo": 0.6,
            "cuajado": 0.9,
            "maduración": 0.7
        }
        return kc_values.get(self.growth_stage.lower(), 0.0)

    def penman_monteith_modified(self, tmax, tmin, tmed, rh_max, rh_min, day_of_year):
        # Cálculo de la presión del aire
        P = 101.3 * (((293 - 0.0065 * self.elevation) / 293) ** 5.26)

        # Cálculo de la radiación neta
        Rn = (0.75 + 2e-5 * self.elevation) * self.extraterrestrial_radiation(day_of_year)

        # Cálculo de la temperatura promedio en Kelvin
        Tmean_K = tmed + 273.15

        # Cálculo de la radiación de onda larga
        Rl = -0.00000005 * Tmean_K ** 4 * (0.34 - 0.14 * math.sqrt((rh_max + rh_min) / 2)) * (1.35 * Rn / self.extraterrestrial_radiation(day_of_year) - 0.35)

        # Cálculo de la radiación neta ajustada
        Rn_adj = Rn + Rl

        # Cálculo de la constante psicométrica
        gamma = 0.665e-3 * P

        # Cálculo del déficit de presión de vapor de saturación
        es = 0.6108 * (math.exp((17.27 * tmed) / (tmed + 237.3)) - math.exp((17.27 * tmin) / (tmin + 237.3)))

        # Cálculo de la humedad relativa promedio
        rh_mean = (rh_max + rh_min) / 2

        # Cálculo del déficit de presión de vapor real
        ea = rh_mean / 100 * es

        # Cálculo de la evapotranspiración de referencia (ETo)
        ETo = (0.408 * (Rn_adj - Rl) * (es - ea) + gamma * 900 / (tmed + 273) * (es - ea)) / (es - ea + gamma * (1 + 0.34 * 2))
        
        return ETo

    def calculate_water_required(self, etc_values, precipitation):
        effective_precipitation = precipitation * 10  # Convert from cm to mm
        water_required = (etc_values - effective_precipitation) / self.irrigation_efficiency
        water_required_liters = water_required * 1000  # Convert from m^3 to liters (assuming 1 ha area)
        water_required_liters = water_required_liters.clip(lower=0)  # Set a lower limit of 0
        return water_required_liters

