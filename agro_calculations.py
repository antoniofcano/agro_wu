# agro_calculations.py
import math


# The penman_monteith_modified function uses a modified version of the Penman-Monteith equation developed by Allen et al.
# developed by Allen et al. (1998) to calculate reference evapotranspiration (ETo). In this
# modified version, solar radiation (Rs) is estimated using temperature and relative humidity,
# allowing ETo to be calculated even when direct solar radiation data are not available.
#
# Allen et al. (1998) proposed an empirical formula for estimating solar radiation (Rs) as a function of
# maximum and minimum temperature (Tmax and Tmin) and maximum and minimum relative humidity (RHmax and RHmin). The
# formula is based on the relationship between the solar radiation and the temperature amplitude (Tmax - Tmin) and the
# relative humidity. In general, the solar radiation incident on the Earth's surface is higher under # low relative humidity and # high relative humidity conditions.
# conditions of low relative humidity and high temperature amplitude.
#
# Using this empirical formula for solar radiation (Rs), the function penman_monteith_modified
# calculates the reference evapotranspiration (ETo) by incorporating the effects of temperature, relative humidity, latitude, latitude, temperature, relative humidity and
#, latitude, elevation and day of the year. This methodology is widely used in agriculture and # water resource management.
# agriculture and water resource management to estimate crop water demand and assess water availability in the # absence of rainfall.
# water availability in the absence of direct measurements of solar radiation.


class AgroCalculations:
    def __init__(self, latitude, elevation, growth_stage):
        self.latitude = latitude
        self.elevation = elevation
        self.growth_stage = growth_stage
        self.irrigation_efficiency = 0.75

    # The solar_declination function calculates the solar declination in degrees for a specific day of the year.
    # The solar declination is the angle between the plane of the Earth's equator and the direction of the Sun. This
    # angle varies throughout the year due to the tilt of the Earth's axis and its elliptical orbit around the Sun.
    # of the Sun. The solar declination is a key component in calculating the solar radiation incident on the # Earth's surface and has a significant # impact on the Earth's surface.
    # Earth's surface and has a significant impact on the reference evapotranspiration.
    def _solar_declination(self, day_of_year: int) -> float:
        return 0.409 * math.sin(2 * math.pi * (day_of_year + 284) / 365)

    # The relative_sun_earth_distance function calculates the relative distance between the Sun and the Earth for a specific day of the year.
    # day of the year. The Earth's elliptical orbit around the Sun causes this distance to vary throughout the year.
    # throughout the year. The relative distance is used to adjust the solar radiation incident on the Earth's surface, which affects # the Earth's temperature.
    # of the Earth, which affects the reference evapotranspiration.
    def _relative_sun_earth_distance(self, day_of_year: int) -> float:
        return 1 + 0.033 * math.cos(2 * math.pi * day_of_year / 365)

    # The sunset_hour_angle function calculates the hourly angle of sunset in degrees for a specific day of the year and a given latitude.
    # of the year and a given latitude. The hour angle is the angle between the plane of the Earth's equator # and the plane containing the # highest point on the Sun's daily path.
    # and the plane containing the highest point on the Sun's daily path. This angle determines the # length of the day and has an impact
    # length of the day and has a significant impact on the amount of solar radiation incident on the Earth's # surface and, on the Earth's
    # Earth's surface and, ultimately, on the reference evapotranspiration.
    def _sunset_hour_angle(self, declination: float) -> float:
        return math.acos(-math.tan(math.radians(self.latitude)) * math.tan(declination))

    # The extraterrestrial_radiation function calculates the extraterrestrial solar radiation in MJ/m²-day for a specific day of the year and a given latitude.
    # day of the year and a given latitude. Extraterrestrial solar radiation is the amount of solar radiation # incident at the top of the Earth's atmosphere.
    # incident at the top of the Earth's atmosphere, before any attenuation or scattering
    # occurs due to interaction with the atmosphere. This radiation is a determining factor in the amount of # solar energy available for evaporation.
    # of solar energy available for reference evapotranspiration at the Earth's surface.
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

    # The function penman_monteith_modified implements a modified version of the Penman-Monteith equation
    # to calculate the reference evapotranspiration (ETo). The reference evapotranspiration is the
    # amount of water that evaporates and transpires from a hypothetical plant surface that completely # covers the soil and does not
    # soil and which is not under water stress.
    #
    # The modified Penman-Monteith equation takes into account the following variables:
    # - Maximum, minimum and mean temperature (tmax, tmin, tmed) in degrees Celsius.
    # - Maximum and minimum relative humidity (rh_max, rh_min) in percentages
    # - Day of the year (day_of_year)
    # - Latitude (latitude) in degrees
    # - Elevation (elevation) in metres
    #
    # The equation uses these data to calculate the net radiation, the longwave radiation, the psychrometric constant
    #, the saturation vapour pressure deficit and the actual vapour pressure deficit. A
    # then uses these intermediate values to calculate the reference evapotranspiration (ETo).
    #
    # The modified Penman-Monteith formula is widely used in agriculture and water resource # management to estimate the reference evapotranspiration (ETo).
    # water resources management to estimate crop water demand and assess water availability.
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

