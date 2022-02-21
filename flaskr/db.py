import sqlite3
from turtle import home

import datetime
import click
import pandas as pd
from flask import current_app, g
from flask.cli import with_appcontext

# Set up database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.close()
        
# Initialise db and load data from excel file
def init_db():
    db = get_db()
    
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))
    
    # Read excel    
    flights = pd.read_excel("./flaskr/flights.xlsx")
    
    # Rename columns
    flights = flights.rename(columns={
        "Flight": "flight_name",
        "Departure": "departure_city",
        "Arrival": "arrival_city",
        "DepartureTime": "departure_time",
        "ArrivalTime": "arrival_time",
        "Schedule": "schedule",
        "Price": "price",
        "Days": "additional_days"
    })
    
    # Populate SQL tables
    flights.to_sql(
        'flights',
        db,
        if_exists='append',
        index=False
    )

@click.command('init-db')
@with_appcontext
def init_db_command():
    # Clear existing data and create new tables
    init_db()
    click.echo("Initialized the database")
    
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def getCursor():
    return get_db().cursor()

# Get flights from database. Returns flights in a list
def getFlights():
    cursor = getCursor()
    
    flights = []
    
    cursor.execute('SELECT * FROM flights')
    
    for row in cursor:
        flight = dict()
        flight['id'] = row['id']
        flight['flight_name'] = row['flight_name']
        flight['departure_city'] = row['departure_city']
        flight['arrival_city'] = row['arrival_city']
        flight['departure_time'] = row['departure_time']
        flight['arrival_time'] = row['arrival_time']
        flight['schedule'] = row['schedule']
        flight['price'] = row['price']
        flight['additional_days'] = row['additional_days']
        
        flights.append(flight)
    
    cursor.close()
    return flights

def next4days(x):
    ans = []
    for i in range(x, x+4):
        ans.append(i % 7)
    return ans

def parseResultRowWithDate(row, date):
    flight = {}
    # flight['id'] = row['id']
    flight['flight_name'] = row['flight_name']
    flight['departure_city'] = row['departure_city']
    flight['arrival_city'] = row['arrival_city']
    flight['departure_time'] = row['departure_time']
    flight['arrival_time'] = row['arrival_time']
    flight['date'] = date
    flight['price'] = row['price']
    # flight['additional_days'] = row['additional_days']
    return flight

# Gets best departure and return flights based on a start and end date
# Assume direct flights only
def getBestFlights(startDate: datetime, endDate: datetime):
    cursor = getCursor()
    startDay = startDate.weekday()
    startWindow = next4days(startDay)
    
    # Get cheapest departure flight in the next 4 days
    cursor.execute('SELECT * FROM flights WHERE departure_city = "Singapore" AND arrival_city = "Incheon"')
    startFlights = []
    for row in cursor:
        schedule = str(row['schedule']).split(',')
        schedule = [int(x)-1 for x in schedule]
        for day in schedule:
            if day in startWindow:
                date = startDate + datetime.timedelta(days=startWindow.index(day))
                startFlights.append(parseResultRowWithDate(row, date))
                break
    
    startFlights.sort(key=lambda x: x['price'])
    startFlight = startFlights[0]
    
    # Get best return flight
    delta = startFlight['date'] - startDate
    endDate = endDate + datetime.timedelta(days = delta.days)
    endDay = endDate.weekday()
    cursor.execute('SELECT * FROM flights WHERE departure_city = "Incheon" AND arrival_city = "Singapore"')
    returnFlights = []
    returnWindow = next4days(endDay)
    for row in cursor:
        schedule = str(row['schedule']).split(',')
        schedule = [int(x)-1 for x in schedule]
        for day in schedule:
            if day in returnWindow:
                date = endDate + datetime.timedelta(days=returnWindow.index(day))
                returnFlights.append(parseResultRowWithDate(row, date))
                break
    returnFlights.sort(key=lambda x: x['price'])
    returnFlight = returnFlights[0]

    startFlight['date'] = startFlight['date'].strftime('%Y-%m-%d')
    returnFlight['date'] = returnFlight['date'].strftime('%Y-%m-%d')
    
    return [startFlight, returnFlight]
        
    
