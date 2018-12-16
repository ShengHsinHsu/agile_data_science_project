from flask import Flask, render_template, request
from pymongo import MongoClient
from util import es_helper
import config
## Dump the mongo result to the json
#from bson import json_util

# Set up Flask and Mongo
app = Flask(__name__)
client = MongoClient()


# Controller: Fetch a  flight and display it
@app.route("/on_time_performance")
def on_time_performance():
    ## Example of API
    # "Carrier" : "F9",
    # "FlightDate" : "2015-11-03",
    # "FlightNum" : "262"
    carrier = request.args.get('Carrier')
    flight_date = request.args.get('FlightDate')
    flight_num = request.args.get('FlightNum')

    flight = client.agile_data_science.on_time_performance.find_one({
        'Carrier': carrier,
        'FlightDate': flight_date,
        'FlightNum': flight_num
    })

    return render_template('flight.html', flight=flight)

# Controller: Fetch all flight between cities on a given day and display them
@app.route("/flights/<origin>/<dest>/<flight_date>")
def list_flights(origin, dest, flight_date):
    # The example of API: /flights/SNA/DEN/2015-11-03
    # 'Origin': SNA,
    # 'Dest': DEN
    # 'FlightDate': 2015-11-03

    start = request.args.get('start') or 0
    end = request.args.get('end') or 20

    start = max(int(start) -1, 0)
    end = int(end)
    width = end - start


    flights = client.agile_data_science.on_time_performance.find({
        'Origin': origin,
        'Dest': dest,
        'FlightDate': flight_date
    },
        sort =[
            ('DepTime', 1),
            ('ArrTime', 1),
    ])
    # Above is pagination
    flights.skip(start).limit(width)

    flight_count = flights.count()
    nav_offsets = es_helper.get_navigation_offsets(start, end, config.RECORDS_PER_PAGE)


    return render_template(
        'flights.html',
        flights=flights,
        flight_date=flight_date,
        flight_count=flight_count,
        nav_path=request.path,
        nav_offsets=nav_offsets
    )



if __name__ == "__main__":
    app.run(debug=True)
