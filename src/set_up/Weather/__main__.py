import json
import os

import geopy.distance
import pandas as pd
from neo4j import GraphDatabase
import settings
import argparse
from utils.utils import read_config

# get namespaces
bigg = settings.namespace_mappings['bigg']
wgs = settings.namespace_mappings['wgs']

def link_ws(driver, ws_subject, l_subject):
    with driver.session() as session:
        session.run(
            f"""
                MATCH(ws:{bigg}__WeatherStation{{uri:"{ws_subject}"}})
                MATCH(l:{bigg}__BuildingSpace{{uri:"{l_subject}"}})
                Merge (l)-[:{bigg}__isObservedByDevice]->(ws)
                RETURN l
            """
        )


def create_ws(driver, stations, ns):
    with driver.session() as session:
        for _, s in stations.iterrows():
            subject = f"{ns}{float(s.latitude):.3f}~{float(s.longitude):.3f}"
            session.run(
                f"""
                       MERGE (ws:{bigg}__WeatherStation:{wgs}__SpatialThing:Resource{{uri:"{subject}"}})
                       SET ws.{wgs}__lat="{float(s.latitude):.3f}", ws.{wgs}__long="{float(s.longitude):.3f}",
                           ws.source="Darksky"
                       RETURN ws
                   """
            )


def get_ws_locations(driver):
    with driver.session() as session:
        location = session.run(
            f"""
                   Match(n:{bigg}__WeatherStation) return n.uri as subject, n.{wgs}__lat as latitude, n.{wgs}__long as longitude
               """
        ).data()
        return location


def get_building_locations_lat_lon(driver, namespaces):
    with driver.session() as session:
        location = session.run(
            f"""
                Match (bs:{bigg}__BuildingSpace)<-[]-(n:{bigg}__Building)-[:{bigg}__hasLocationInfo]->(l:{bigg}__LocationInfo)
                WHERE l.{bigg}__addressLatitude IS NOT NULL and l.{bigg}__addressLongitude IS NOT NULL AND split(l.uri,"#")[0] in {namespaces}
                RETURN bs.uri AS subject, toFloat(l.{bigg}__addressLatitude) AS latitude, toFloat(l.{bigg}__addressLongitude) AS longitude
            """
        ).data()
    return location


def get_building_locations_stations_df(driver, stations_df, query,  namespaces, correction_function = None):
    location = []
    with driver.session() as session:
        buildings = session.run(
           query.format(**dict(locals(), **globals()))
        ).data()
    for b in buildings:
        lat, lon = (None, None)
        try:
            lat, lon = stations.loc[b['station_code']][['latitude', 'longitude']].items()
        except:
            if correction_function:
                lat, lon = correction_function(b)

        if any([not lat, not lon]):
            print(f"station {b['station_code']} does not exist")
            continue
        location.append({"subject": b['subject'], "latitude": lat[1], "longitude": lon[1]})
    return location


def get_distance(x, lat, lon):
    return geopy.distance.distance((x['latitude'], x['longitude']), (lat, lon)).km


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create of Weather Stations to neo4j.')
    parser.add_argument("-f", "--file", help="The file containing weather stations with location", required=True)
    parser.add_argument("-namespace", "-n", help="The namespace for the weather stations", required=True)
    parser.add_argument("--country", "-cn", help="Country to use", required=True)
    parser.add_argument("--create", "-c", help="create the weather stations", action='store_true')
    parser.add_argument("--update", "-u", help="update the links of buildings with weather stations", action='store_true')
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-f", "data/Weather/cpcat.json", "-n", "https://weather.beegroup-cimne.com#", "-cn", "ES", "-c", "-u"]
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()

    config = read_config(settings.conf_file)

    driver = GraphDatabase.driver(**config['neo4j'])
    with open(args.file) as f:
        cpcat = json.load(f)

    stations = pd.DataFrame.from_dict(cpcat, orient="index")
    stations.columns = ["latitude", "longitude"]
    if args.create:
        create_ws(driver, stations, args.namespace)
    if args.update:
        country_info = settings.COUNTRIES[args.country]
        location1 = pd.DataFrame(get_building_locations_lat_lon(driver, namespaces=country_info['namespaces']))
        location2 = pd.DataFrame(get_building_locations_stations_df(driver, stations, country_info['weather_query'],
                                                                    namespaces=country_info['namespaces']))
        if location1.empty:
            location = location2
        elif location2.empty:
            location = location1
        else:
            location = location1.merge(location2.drop_duplicates(), on=['subject'], how='outer', indicator=True)
            location['latitude'] = location.apply(lambda x: x['latitude_x'] if x['_merge'] in ['left_only', 'both'] else x['latitude_y'], axis=1)
            location['longitude'] = location.apply(lambda x: x['longitude_x'] if x['_merge'] in ['left_only', 'both'] else x['longitude_y'], axis=1)

        if not location.empty:

            location = location[(pd.isna(location.latitude) | pd.isna(location.longitude)) == False]
            ws = pd.DataFrame(get_ws_locations(driver))

            from math import sin, cos, sqrt, atan2, radians

            ws['latitude'] = ws['latitude'].apply(lambda x: radians(float(x)))
            ws['longitude'] = ws['longitude'].apply(lambda x: radians(float(x)))

            location['latitude'] = location['latitude'].apply(lambda x: radians(float(x)))
            location['longitude'] = location['longitude'].apply(lambda x: radians(float(x)))

            for _, l in location.iterrows():
                ws['dist'] = ws.apply(get_distance, lat=l['latitude'], lon=l['longitude'], axis=1)
                ws_sel = ws[ws.dist == ws.dist.min()]
                if ws_sel.dist.values[0] < 400:
                    link_ws(driver, ws_sel.subject.values[0], l['subject'])
        driver.close()
