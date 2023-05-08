import os
import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from agro_calculations import AgroCalculations



Base = declarative_base()


class RegistroMeteorologico(Base):
    __tablename__ = 'registro_meteorologico'

    id = Column(Integer, primary_key=True)
    obsTimeUtc = Column(Date, nullable=False)
    temp_max = Column(Float, nullable=False)
    temp_min = Column(Float, nullable=False)
    temp_med = Column(Float, nullable=False)
    hum_max = Column(Float, nullable=False)
    hum_min = Column(Float, nullable=False)
    prec = Column(Float, nullable=False)
    etc = Column(Float, nullable=False)
    day_of_year =  Column(Float, nullable=False) 
    water_req = Column(Float, nullable=False)


    def __repr__(self):
        return f"<RegistroMeteorologico(obsTimeUtc={self.obsTimeUtc}, temp_max={self.temp_max}, temp_min={self.temp_min}, temp_med={self.temp_med}, hum_max={self.hum_max}, hum_min={self.hum_min}, 
prec={self.prec}, day_of_year={self.day_of_year}, etc={self.etc}, water_req={self.water_req})>"


class GestorBBDD:
    def __init__(self, db_name: str, table_name: str, estacion: EstacionMeteorologica, latitude: float, elevation: float, growth_stage: str):
        self.engine = create_engine(f"sqlite:///{db_name}.db")
        self.table_name = table_name
        self.estacion = estacion
        self.calculations = AgroCalculations(latitude, elevation, growth_stage)
        self.Session = sessionmaker(bind=self.engine)

    def get_data(self):
        with self.engine.connect() as connection:
            result = connection.execute(text(f"SELECT * FROM {self.table_name}"))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df

    def actualizar_datos(self):
        session = self.Session()

        fecha_actual = datetime.datetime.now().date()
        ultimo_registro = session.query(RegistroMeteorologico).order_by(RegistroMeteorologico.obsTimeUtc.desc()).first()

        if ultimo_registro:
            fecha_ultimo_registro = ultimo_registro.obsTimeUtc.date()
        else:
            fecha_ultimo_registro = datetime.date(2021, 1, 1)

        if fecha_ultimo_registro < fecha_actual:
            estacion = EstacionMeteorologica(self.api_key, self.station_id)
            estacion.obtener_datos_estacion(fecha_ultimo_registro + datetime.timedelta(days=1))
            estacion.limpieza_datos()
            datos_actualizados = estacion.get_datos()

            if not datos_actualizados.empty:
                registros_nuevos = []
                for index, row in datos_actualizados.iterrows():
                    registro = RegistroMeteorologico(
                        obsTimeUtc=row['obsTimeUtc'],
                        # Agregar más columnas según sea necesario
                        temp_max=row['temp_max'],
                        temp_min=row['temp_min'],
                        temp_med=row['temp_med'],
                        hum_max=row['hum_max'],
                        hum_min=row['hum_min'],
                        day_of_year = row['day_of_year'],
                        prec=row['prec'],
                        etc = self.calculations.penman_monteith_modified(temp_max, temp_min, temp_med, hum_max, hum_min, day_of_year)
                        water_required = self.calculations.calculate_water_required(etc, prec)
                    )
                    registros_nuevos.append(registro)

                session.add_all(registros_nuevos)
                session.commit()

        session.close()

