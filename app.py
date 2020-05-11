##------Import library--------------------------------------------
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,inspect
import datetime as dt
from flask import Flask,jsonify

##--------Database Set-Up------------------------------------------
engine = create_engine('sqlite:///Resources/hawaii.sqlite')
Base =automap_base()
Base.prepare(engine,reflect=True)

measurement =Base.classes.measurement
station = Base.classes.station


##---------Flask Routes ---------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    print('Welcome to my Home Page! This is my Climate Analysis')
    return (f'Available Routes:<br/>'
            f'/api/v1.0/precipitation<br/>'
            f'/api/v1.0/stations<br/>'
            f'/api/v1.0/tobs<br/>'
            f'/api/v1.0/tobs/start<br/>'
            f'/api/v1.0/tobs/start/end')

@app.route('/api/v1.0/precipitation')
def precipitation():
    session=Session(engine)
    query = session.query(measurement.date,measurement.prcp).all()
    session.close()
    precip_data =[]
    for date,prcp in query:
        prep_dict ={}
        prep_dict['Date']=date
        prep_dict['Precipitation']=prcp
        precip_data.append(prep_dict)
    return jsonify(precip_data)

@app.route('/api/v1.0/stations')
def stations():
    session=Session(engine)
    query=session.query(measurement.station.distinct()).all()
    session.close()
    station_list = list(np.ravel(query))
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    session=Session(engine)
    latestdate = session.query(measurement.date).order_by(measurement.date.desc()).first()
    session.close()
##----Most Active Station ----------------------------------------------------------------------------------------
    # row_count = func.count(measurement.station)
    # active_station = session.query(measurement.station,row_count).\
    #                 group_by(measurement.station).\
    #                 order_by(row_count.desc()).all()
    # active_station_list=[]
    # for station,row_counts in active_station:
    #     station_list={}
    #     station_list['Station']=station
    #     station_list['Counts of Observed Data Points']=row_counts
    #     active_station_list.append(station_list)
    
##----Temperature Observation for Most Active Station ----------------------------------------------------------------------------------------
    query_date = (dt.datetime.strptime(latestdate[0],'%Y-%m-%d') - dt.timedelta(days=366)).strftime('%Y-%m-%d')
    standout_station = session.query(measurement.station,measurement.date,measurement.tobs).\
                    filter(measurement.station=='USC00519281').\
                    filter(measurement.date>query_date).all()
    standout_station_list=[]
    for stations,date,tobs in standout_station:
        standout={}
        standout['Stations']=stations
        standout['Date']=date
        standout['TOBS']=tobs
        standout_station_list.append(standout)
    return jsonify(standout_station_list)
    

# @app.route('/api/v1.0/tobs/<start>')
# def tobs_start(start):
#     start_date= start.replace(' ','').replace('/','').replace('-','').strftime('%Y-%M-%d')
#     session=Session(engine)
#     min_query=session.query(measurement.date,func.min(measurement.tobs)).\
#                 filter(measurement.date>=start_date).all()
#     session.close()
#     min_query_list = list(np.ravel(min_query))

#     return jsonify(f'The minimum temperature from {start_date}is:{min_query_list}')

# @app.route('/api/v1.0/tobs/<start>/<end>')
# def tobs_start_end(start,end):

#     return 'continue'



if __name__ == '__main__':
    app.run(debug=True)

