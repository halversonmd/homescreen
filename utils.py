import requests
import json
import datetime as dt
from uber_rides.session import Session
from uber_rides.client import UberRidesClient
from google.transit import gtfs_realtime_pb2
import urllib.request

with open('config.txt', 'r') as f:
    config = json.load(f)

def trains():

    def get_time(name):

        home = config["HOME_ADDRESS"]
        works = config["WORKS"]
        depart_time = dt.datetime.now()
        r = requests.get("https://maps.googleapis.com/maps/api/directions/json?origin={home}&destination={work}&mode=transit&key={key}".format(home=home, work=works[name], key=config["GOOGLE_KEY"]))
        data = json.loads(r.text)

        arrive_time = dt.datetime.fromtimestamp(data['routes'][0]['legs'][0]['arrival_time']['value'])
        travel_time = arrive_time - depart_time
        return travel_time.seconds // 60 % 60

    return {'mike':get_time('mike'), 'anne': get_time('anne')}

def uber():

    session = Session(server_token=config["UBER_TOKEN"])
    client = UberRidesClient(session)

    def get_data(name):

        home_lat, home_lon = 40.7709982, -73.9523798
        coords = {'anne':{'lat': 40.7526635, 'lon': -73.9749936},'mike':{'lat': 40.754487, 'lon': -73.9943511}}
        end_lat = coords[name]['lat']
        end_lon = coords[name]['lon']

        response = client.get_price_estimates(
            start_latitude=home_lat,
            start_longitude=home_lon,
            end_latitude=end_lat,
            end_longitude=end_lon,
            seat_count=1
        )

        resp = response.json.get('prices')
        for opt in resp:
            if opt['localized_display_name'] == 'uberX':
                estimate = opt['estimate']
                duration = int(opt['duration']/60)
                response = client.get_pickup_time_estimates(home_lat, home_lon, product_id=opt['product_id'])
                wait_time = int(response.json.get('times')[0]['estimate']/60)
                return {'estimate': estimate, 'duration': duration, 'wait_time':wait_time}

    return {'mike':get_data('mike'), 'anne': get_data('anne')}

def mta():

    def get_times(name):

        if name == 'anne':
            feed_id = '1'
            rte_id = '6'
            stp_id = '627S'
        else:
            feed_id = '16'
            rte_id = '6'
            stp_id = 'Q04S'

        #sudo pip3 install --upgrade gtfs-realtime-bindings
        url = 'http://datamine.mta.info/mta_esi.php?key={key}&feed_id={feed_id}'.format(key=config["MTA_KEY"], feed_id=feed_id)

        feed = gtfs_realtime_pb2.FeedMessage()
        response = urllib.request.urlopen(url)
        feed.ParseFromString(response.read())
        next_trains = []
        for entity in feed.entity:
            for stop in entity.trip_update.stop_time_update:
                if stop.stop_id == stp_id:
                    next_trains.append(dt.datetime.fromtimestamp(stop.arrival.time))
        next_trains.sort()
        return next_trains

    now = dt.datetime.now()
    return {'now':now,'mike': get_times('mike'), 'anne': get_times('anne')}


if __name__ == '__main__':
    
    mta_data = mta()
    print('mta_data', mta_data['anne'])
    