import json
import os
import pandas as pd
from neo4j import GraphDatabase
import settings
import argparse
from utils.utils import read_config


def link_ws(driver, ws_subject, l_subject):
    with driver.session() as session:
        session.run(
            f"""
                MATCH(ws:ns0__WeatherStation{{uri:"{ws_subject}"}})
                MATCH(l:ns0__BuildingSpace{{uri:"{l_subject}"}})
                Merge (l)-[:ns0__isObservedBy]->(ws)
                RETURN l
            """
        )


def create_ws(driver, stations):
    with driver.session() as session:
        for _, s in stations.iterrows():
            subject = f"{args.namespace}{float(s.latitude):.3f}~{float(s.longitude):.3f}"
            session.run(
                f"""
                       MERGE (ws:ns0__WeatherStation:ns0__Device:ns1__SpatialThing{{uri:"{subject}"}})
                       SET ws.ns1__lat="{float(s.latitude):.3f}", ws.ns1__long="{float(s.longitude):.3f}",
                           ws.ns0__weatherStationType="darksky"
                       RETURN ws
                   """
            )


def get_ws_locations(driver):
    with driver.session() as session:
        location = session.run(
            f"""
                   Match(n:ns0__WeatherStation) return n.uri as subject, n.ns1__lat as latitude, n.ns1__long as longitude
               """
        ).data()
        return location


def get_building_locations (driver, stations):
    with driver.session() as session:
        location = session.run(
            f"""
                   Match (bs:ns0__BuildingSpace)<-[]-(n:ns0__Building)-[:ns0__hasLocationInfo]->(l:ns0__LocationInfo)
                   WHERE l.ns0__addressLatitude IS NOT NULL and l.ns0__addressLongitude IS NOT NULL
                   RETURN bs.uri AS subject, toFloat(l.ns0__addressLatitude) AS latitude, toFloat(l.ns0__addressLongitude) AS longitude
               """
        ).data()
        postal_code = session.run(
            f"""
                   Match (bs:ns0__BuildingSpace)<-[]-(n:ns0__Building)-[:ns0__hasLocationInfo]-(l:ns0__LocationInfo) 
                   WHERE l.ns0__addressPostalCode IS NOT NULL and (l.ns0__addressLatitude IS NULL or l.ns0__addressLongitude IS NULL)
                   RETURN bs.uri as subject, l.ns0__addressPostalCode as postal_code
               """
        ).data()
        for cp in postal_code:
            lat, lon = (None, None)
            try:
                lon, lat = stations.loc[cp['postal_code']].items()
            except:
                tries = [1, -1]
                if int(cp['postal_code'][-1]) == 0:
                    tries = [1]
                if int(cp['postal_code'][-1]) == 9:
                    tries = [-1]
                for t in tries:
                    try:
                        test = str(int(cp['postal_code'])+t).zfill(5)
                        lon, lat = stations.loc[test].items()
                        break
                    except:
                        pass
                if any([not lat, not lon]):
                    print(f"postal code {cp['postal_code']} does not exist")
                    continue
            location.append({"subject": cp['subject'], "latitude": lat[1], "longitude": lon[1]})
    return location


def get_distance(x, lat, lon):
    R = 6373.0
    dlon = x['latitude'] - lat
    dlat = x['longitude'] - lon
    a = sin(dlat / 2) ** 2 + cos(lat) * cos(x['latitude']) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create of Weather Stations to neo4j.')
    parser.add_argument("-f", "--file", help="The file containing weather stations with location", required=True)
    parser.add_argument("-namespace", "-n", help="The namespace for the weather stations", required=True)
    parser.add_argument("--create", "-c", help="create the weather stations", action='store_true')
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-f", "data/Weather/cpcat.json", "-n", "https://weather.beegroup-cimne.com#", "-c"]
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()

    config = read_config(settings.conf_file)

    driver = GraphDatabase.driver(**config['neo4j'])
    with open(args.file) as f:
        cpcat = json.load(f)

    stations = pd.DataFrame.from_dict(cpcat, orient="index")
    stations.columns = ["longitude", "latitude"]
    if args.create:
        create_ws(driver, stations)
    location = pd.DataFrame(get_building_locations(driver, stations))
    ws = pd.DataFrame(get_ws_locations(driver))

    from math import sin, cos, sqrt, atan2, radians

    ws['latitude'] = ws['latitude'].apply(lambda x: radians(float(x)))
    ws['longitude'] = ws['longitude'].apply(lambda x: radians(float(x)))

    location['latitude'] = location['latitude'].apply(lambda x: radians(float(x)))
    location['longitude'] = location['longitude'].apply(lambda x: radians(float(x)))

    for _, l in location.iterrows():
        ws['dist'] = ws.apply(get_distance, lat=l['latitude'], lon=l['longitude'], axis=1)
        ws_sel = ws[ws.dist == ws.dist.min()].subject
        link_ws(driver, ws_sel.values[0], l['subject'])
