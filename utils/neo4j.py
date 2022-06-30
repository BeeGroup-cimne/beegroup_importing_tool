
def get_cups_id_link(session, user, ns_mappings):
    bigg = ns_mappings['bigg']
    cups_device = session.run(f"""
        Match (u:{bigg}__UtilityPointOfDelivery)<-[:{bigg}__hasSpace|{bigg}__hasUtilityPointOfDelivery *]-
              (b:{bigg}__Building)<-[:{bigg}__managesBuilding|{bigg}__hasSubOrganization *]-
              (o:{bigg}__Organization{{userID:"{user}"}}) 
        RETURN u.{bigg}__pointOfDeliveryIDFromOrganization as CUPS, b.{bigg}__buildingIDFromOrganization as NumEns
    """)
    return {x['CUPS'][0]: x['NumEns'][0] for x in cups_device}


def get_all_linked_weather_stations(session, ns_mappings):
    bigg = ns_mappings['bigg']
    wgs = ns_mappings['wgs']
    location = session.run(
        f"""
                    Match (n:{bigg}__WeatherStation) 
                    WHERE (n)-[:{bigg}__isObservedByDevice]-(:{bigg}__BuildingSpace) 
                    RETURN n.{wgs}__lat as latitude, n.{wgs}__long as longitude
                """
    ).data()
    return location


def get_weather_stations_by_location(session, lat, long, ns_mappings):
    bigg = ns_mappings['bigg']
    wgs = ns_mappings['wgs']
    weather_stations = session.run(f"""
        Match(d:{bigg}__WeatherStation) WHERE d.{wgs}__lat="{lat}" AND d.{wgs}__long="{long}" return d
    """)
    return weather_stations


def get_device_from_datasource(session, user, device_id, source, ns_mappings):
    bigg = ns_mappings['bigg']
    device_neo = session.run(f"""
                MATCH ({bigg}__Organization{{userID:'{user}'}})-[:{bigg}__hasSubOrganization*0..]->(o:{bigg}__Organization)-
                [:hasSource]->(s:{source})<-[:importedFromSource]-(d)
                WHERE d.source = "{source}" AND d.{bigg}__deviceName = ["{device_id}"] return d            
                """)
    return device_neo


def get_tariff_from_datasource(session, user, device_id, source, ns_mappings):
    bigg = ns_mappings['bigg']
    tariff_neo = session.run(f"""
                MATCH ({bigg}__Organization{{userID:'{user}'}})-[:{bigg}__hasSubOrganization*0..]->(o:{bigg}__Organization)-
                [:hasSource]->(s:{source})<-[:importedFromSource]-(d)
                WHERE d.source = "{source}" AND d.{bigg}__tariffName = ["{device_id}"] return d            
                """)
    return tariff_neo


def get_all_buildings_id_from_datasource(session, source_id, ns_mappings):
    bigg = ns_mappings['bigg']
    buildings_neo = session.run(f"""
        MATCH (n:{bigg}__Building)<-[:{bigg}__managesBuilding]-()<-[:{bigg}__hasSubOrganization *0..]-
                (o:{bigg}__Organization)-[:hasSource]->(s:GemwebSource) 
                    Where id(s)={source_id} 
                    return n.{bigg}__buildingIDFromOrganization""")
    return list(set([x[0][0] for x in buildings_neo.values()]))


def create_timeseries(session, ts_uri, property_uri, is_regular, is_cumulative, is_on_change, freq, agg_func, dt_ini, dt_end,
                      ns_mappings):
    bigg = ns_mappings['bigg']

    def convert(tz):
        if not tz.tz:
            tz = tz.tz_localize("UTC")
        if "UTC" != tz.tz.tzname(tz):
            tz = tz.tz_convert("UTC")
        return tz

    session.run(f"""
           MATCH (mp: {bigg}__MeasuredProperty {{uri:"{property_uri}"}})
           MERGE (s: {bigg}__TimeSeries:Resource {{
               uri: "{ts_uri}"
           }})
           Merge(s)-[:{bigg}__hasMeasuredProperty]->(mp)
           SET
               s.{bigg}__timeSeriesIsCumulative= [{is_cumulative}],
               s.{bigg}__timeSeriesIsRegular= [{is_regular}],
               s.{bigg}__timeSeriesIsOnChange= [{is_on_change}],
               s.{bigg}__timeSeriesFrequency= ["{freq}"],
               s.{bigg}__timeSeriesTimeAggregationFunction= ["{agg_func}"],
               s.{bigg}__timeSeriesStart = CASE 
                   WHEN s.{bigg}__timeSeriesStart[0] < 
                    datetime("{convert(dt_ini).to_pydatetime().isoformat()}") 
                       THEN s.{bigg}__timeSeriesStart[0] 
                       ELSE [datetime("{convert(dt_ini).to_pydatetime().isoformat()}")] 
                   END,
               s.{bigg}__timeSeriesEnd = CASE 
                   WHEN s.{bigg}__timeSeriesEnd[0] >
                    datetime("{convert(dt_end).to_pydatetime().isoformat()}") 
                       THEN s.{bigg}__timeSeriesEnd[0]
                       ELSE [datetime("{convert(dt_end).to_pydatetime().isoformat()}")]
                   END  
           return s
       """)


def create_sensor(session, device_uri, sensor_uri, unit_uri, property_uri, estimation_method_uri, measurement_uri,
                  is_regular, is_cumulative, is_on_change, freq, agg_func, dt_ini, dt_end, ns_mappings):

    create_timeseries(session, sensor_uri, property_uri, is_regular, is_cumulative, is_on_change, freq,
                      agg_func, dt_ini, dt_end, ns_mappings)

    bigg = ns_mappings['bigg']
    session.run(f"""
        MATCH (device: {bigg}__Device {{uri:"{device_uri}"}})
        MATCH (msu: {bigg}__MeasurementUnit {{uri:"{unit_uri}"}})
        MATCH (se: {bigg}__SensorEstimationMethod {{uri:"{estimation_method_uri}"}})
        MATCH (s {{uri:"{sensor_uri}"}})   
        MERGE (s)<-[:{bigg}__hasSensor]-(device)
        Merge(s)-[:{bigg}__hasMeasurementUnit]->(msu)
        Merge(s)-[:{bigg}__hasSensorEstimationMethod]->(se)        
        Merge(s)-[:{bigg}__hasMeasurement]->(ms: {bigg}__Measurement:Resource{{uri: "{measurement_uri}"}})
        SET
            s : {bigg}__Sensor
        return s
    """)


def create_tariffPrice(session, tariff_uri, tariffPrice_uri, unit_uri, property_uri, measurement_uri,
                  is_regular, is_cumulative, is_on_change, freq, agg_func, dt_ini, dt_end, ns_mappings):

    create_timeseries(session, tariffPrice_uri, property_uri, is_regular, is_cumulative, is_on_change, freq,
                      agg_func, dt_ini, dt_end, ns_mappings)

    bigg = ns_mappings['bigg']
    session.run(f"""
        MATCH (tariff: {bigg}__Tariff {{uri:"{tariff_uri}"}})
        MATCH (msu: {bigg}__MeasurementUnit {{uri:"{unit_uri}"}})
        MATCH (s {{uri:"{tariffPrice_uri}"}})   
        MERGE (s)<-[:{bigg}__hasTariffPrice]-(device)
        Merge(s)-[:{bigg}__hasTariffCurrencyUnit]->(msu)
        Merge(s)-[:{bigg}__hasTariffValue]->(ms: {bigg}__TariffPoint:Resource{{uri: "{measurement_uri}"}})
        SET
            s : {bigg}__TariffPrice
        return s
    """)
