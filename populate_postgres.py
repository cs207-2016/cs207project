#!/usr/bin/env python3
import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, BigInteger
import random
from timeseries.storagemanager import FileStorageManager
from timeseries.smtimeseries import SMTimeSeries

user = 'cs207site'
password = 'cs207isthebest'
host = 'localhost'
port = '5432'
dbname = 'timeseries'
url = 'postgresql://{}:{}@{}:{}/{}'
url = url.format(user, password, host, port, dbname)
db = create_engine(url)

DIR_NAME = '/var/dbserver/tsdata'

Base = declarative_base()


class TimeseriesEntry(Base):
        """A single timeseries dataset in the timeseries database.
        Contains the following columns:
            id - int - The unique identifier of the timeseries (generated by SQL)
            blarg - float - A random metadata value sampled from [0,1]
            level - char - Randomly selected letter between A and F
            mean - float - Average value of the timeseries
            std - float - Standard deviation of the timeseries
            fpath - string - File path to the time series file (NEEDS TO BE REPLACED WITH STORAGE MANAGER)
    """
        __tablename__ = 'timeseries'

        id = Column(String(30), primary_key=True)
        blarg = Column(Float, nullable=False)
        level = Column(String(1), nullable=False)
        mean = Column(Float, nullable=False)
        std = Column(Float, nullable=False)
        fpath = Column(String(80), nullable=False)

        def __repr__(self):
                return '<ID %d, blarg %f, level %s>' % (self.id, self.blarg, self.level)

Base.metadata.create_all(db)
Session = sessionmaker(bind=db)

if __name__ == '__main__':
        session=Session()
        #ts_entry = TimeseriesEntry(id=0, blarg=0.5, level='E', mean=0, std=0, fpath='hd')
        #session.add(ts_entry)
        fsm = FileStorageManager(DIR_NAME)
        for filename in os.listdir(DIR_NAME):
                if filename.endswith(".npy"):
                        #id from filename
                        tsid=filename.strip('.npy')
                        print(tsid)
                        ts = SMTimeSeries.from_db(tsid, fsm)
                        mean=ts.mean()
                        std=ts.std()
                        level=random
                        blarg = random.random()
                        level = random.choice(["A", "B", "C", "D", "E", "F"])
                        fpath=filename
                        prod = TimeseriesEntry(id=tsid, blarg=blarg, level=level, mean=mean, std=std, fpath=fpath)
                        session.add(prod)
        session.commit()
