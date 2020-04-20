from sqlalchemy import Column, ForeignKey, Integer, String, Float, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import yaml
from sqlalchemy_utils import database_exists

Base = declarative_base()


class NtcResistor(Base):
    __tablename__ = "ntcresistor"

    id = Column(String, primary_key=True)
    resistance = Column(Integer)
    tolerance = Column(Integer)
    betta = Column(Integer)
    bettaTolerance = Column(Integer)


class shunt(Base):
    __tablename__ = "shunt"

    id = Column(String, primary_key=True)
    resistance = Column(Integer)
    tolerance = Column(Integer)


class powerSuply(Base):
    __tablename__ = "powersuply"

    id = Column(String, primary_key=True)
    voltage = Column(Float)
    settlingtime = Column(Float)


class adc(Base):
    __tablename__ = "adc"

    id = Column(String, primary_key=True)
    samplingSpeed = Column(String)
    impedance = Column(String)
    clockFreq = Column(Integer)


class refVoltage(Base):
    __tablename__ = "refvoltage"

    id = Column(String, primary_key=True)
    voltage = Column(Float)


class activeConfiguration(Base):
    __tablename__ = "activeconfiguration"

    id = Column(Integer, primary_key=True)
    ntcresistor = Column(String, ForeignKey("ntcresistor.id"))
    shunt = Column(String, ForeignKey("shunt.id"))
    powerSuply = Column(String, ForeignKey("powersuply.id"))
    adc = Column(String, ForeignKey("adc.id"))
    refVoltage = Column(String, ForeignKey("refvoltage.id"))


def populate_database(Base, engine):
    Session = sessionmaker(bind=engine)
    ses = Session()

    conn = engine.connect()

    with open("config.yaml") as c:
        config = yaml.safe_load(c)

    for k, f in config.get("database").items():
        print("Table {}\n".format(k))
        ins = Base.metadata.tables[k].insert().values(f)
        for key, value in f.items():
            if isinstance(value, list):
                value = ",".join(list(map(str, value)))
            print("column: {}, values: {}".format(key, value))
            f[key] = value
        print(f)
        ins = Base.metadata.tables[k].insert().values(f)
        conn.execute(ins)

    ses.commit()


def make_database(Base, engine):
    return Base.metadata.create_all(engine)


if __name__ == "__main__":
    engine = create_engine("sqlite:///sqlalchemy_example.db")
    if not database_exists(engine.url):
        make_database(Base, engine)
        populate_database(Base, engine)
