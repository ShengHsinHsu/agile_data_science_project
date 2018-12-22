from flask import Flask, render_template, request
from pymongo import MongoClient
from util import es_helper
import config
from bson import json_util
from pyelasticsearch import ElasticSearch


elastic = ElasticSearch(config.ELASTIC_URL)


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


@app.route('/flights/search')
def search_flights():
    # Search Parameters
    critieria_list = ['Carrier', 'FlightDate', 'Origin', 'Dest', 'TailNum', 'FlightNum']
    search_critieria = {}
    for critieria in critieria_list:
        if critieria in request.args:
            search_critieria[critieria] = request.args.get(critieria)


    start = request.args.get('start') or 0
    start = int(start)
    end = request.args.get('end') or config.RECORDS_PER_PAGE
    end = int(end)

    nav_offsets = es_helper.get_navigation_offsets(start, end, config.RECORDS_PER_PAGE)

    query = es_helper.build_query()
    query = es_helper.set_search_critieria(search_critieria, query)
    query = es_helper.set_pagination(start, config.RECORDS_PER_PAGE, query)
    query = es_helper.set_sorting(['FlightDate', 'DepTime', 'Carrier', 'FlightNum'], query)

    results = elastic.search(query)
    flights, flight_count = es_helper.process_search(results)

    return render_template(
        'search.html',
        flights=flights,
        flight_date=search_critieria['FlightDate'],
        flight_count=search_critieria['FlightDate'],
        nav_path=request.path,
        nav_offsets=nav_offsets,
        carrier=search_critieria['Carrier'],
        origin=search_critieria['Origin'],
        dest=search_critieria['Dest'],
        tail_number=search_critieria['TailNum'],
        flight_number=search_critieria['FlightNum']
    )


# Controller: Fetch a flight chart
@app.route("/total_flights")
def total_flights():
    total_flight = client.agile_data_science.flights_by_month.find({}, sort=[('Year', 1), ('Month', 1)])
    response = []
    for item in total_flight:
        dic = {
            'Year': int(item['Year']),
            'Month': int(item['Month']),
            'total_flights': item['total_flights']
        }
        response.append(dic)

    return render_template('total_flights.html', total_flights=response)


# Controller: Fetch a flight chart
@app.route("/total_flights_chart")
def total_flights_chart():
    total_flight = client.agile_data_science.flights_by_month.find({}, sort=[('Year', 1), ('Month', 1)])
    response = []
    for item in total_flight:
        dic = {
            'Year': int(item['Year']),
            'Month': int(item['Month']),
            'total_flights': item['total_flights']
        }
        response.append(dic)
    return render_template('total_flights_chart.html', total_flights=response)


# Serve the chart's data via an asynchronous request (formerly known as 'AJAX')
@app.route("/total_flights.json")
def total_flight_json():
    total_flight = client.agile_data_science.flights_by_month.find({}, sort=[('Year', 1), ('Month', 1)])
    response = []
    for item in total_flight:
        dic = {
            'Year': int(item['Year']),
            'Month': int(item['Month']),
            'total_flights': item['total_flights']
        }
        response.append(dic)
    return json_util.dumps(response, ensure_ascii=False)


# Controller: Fetch a flight and display it
@app.route('/airplane/flights/<tail_number>')
def flights_per_airplane(tail_number):
    flights = client.agile_data_science.flights_per_airplane.find_one({"TailNum": tail_number})

    return render_template('flights_per_airplane.html', flights=flights, tail_number=tail_number)


if __name__ == "__main__":
    app.run(debug=True)
