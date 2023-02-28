def get_cups_id_link(session, user, ns_mappings):
    bigg = ns_mappings['bigg']
    cups_device = session.run(f"""
        Match (u:{bigg}__UtilityPointOfDelivery)<-[:{bigg}__hasSpace|{bigg}__hasUtilityPointOfDelivery *]-
              (b:{bigg}__Building)<-[:{bigg}__managesBuilding|{bigg}__hasSubOrganization *]-
              (o:{bigg}__Organization{{userID:"{user}"}}) 
        RETURN u.{bigg}__pointOfDeliveryIDFromOrganization as CUPS, b.{bigg}__buildingIDFromOrganization as NumEns
    """)
    return {x['CUPS']: x['NumEns'] for x in cups_device}


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
                WHERE d.source = "{source}" AND d.{bigg}__deviceName = "{device_id}" return d            
                """)
    return device_neo


def get_tariff_from_datasource(session, user, device_id, source, ns_mappings):
    bigg = ns_mappings['bigg']
    tariff_neo = session.run(f"""
                MATCH ({bigg}__Organization{{userID:'{user}'}})-[:{bigg}__hasSubOrganization*0..]->(o:{bigg}__Organization)-
                [:hasSource]->(s:{source})<-[:importedFromSource]-(d)
                WHERE d.uri = "{device_id}" return d            
                """)
    return tariff_neo


def get_co2_from_datasource(session, station_id, ns_mappings):
    bigg = ns_mappings['bigg']
    tariff_neo = session.run(f"""
                MATCH (d:{bigg}__CO2EmissionsFactor{{uri: "{station_id}"}})
                RETURN d            
                """)
    return tariff_neo

def get_device_by_uri(session, uri):
    query = f"""
    match(d:bigg__Device)-[:bigg__hasSensor]-(s) where d.uri = "{uri}" return d,s
    """
    value = list(session.run(query))
    return value[0] if value else None


def get_all_buildings_id_from_datasource(session, source_id, ns_mappings):
    bigg = ns_mappings['bigg']
    buildings_neo = session.run(f"""
        MATCH (n:{bigg}__Building)<-[:{bigg}__managesBuilding]-()<-[:{bigg}__hasSubOrganization *0..]-
                (o:{bigg}__Organization)-[:hasSource]->(s) 
                    Where id(s)={source_id} 
                    return n.{bigg}__buildingIDFromOrganization""")
    return list(set([x[0] for x in buildings_neo.values()]))


def create_timeseries(session, ts_uri, property_uri, estimation_method_uri, is_regular, is_cumulative, is_on_change,
                      freq, agg_func, dt_ini, dt_end, ns_mappings):

    bigg = ns_mappings['bigg']

    def convert(tz):
        if not tz.tz:
            tz = tz.tz_localize("UTC")
        if "UTC" != tz.tz.tzname(tz):
            tz = tz.tz_convert("UTC")
        return tz

    session.run(f"""
           MATCH (mp: {bigg}__MeasuredProperty {{uri:"{property_uri}"}})
           MATCH (se: {bigg}__EstimationMethod {{uri:"{estimation_method_uri}"}})

           MERGE (s: {bigg}__TimeSeriesList:Resource {{
               uri: "{ts_uri}"
           }})
           Merge(s)-[:{bigg}__hasMeasuredProperty]->(mp)
           Merge(s)-[:{bigg}__hasEstimationMethod]->(se)        
           SET
               s.{bigg}__timeSeriesIsCumulative= {is_cumulative},
               s.{bigg}__timeSeriesIsRegular= {is_regular},
               s.{bigg}__timeSeriesIsOnChange= {is_on_change},
               s.{bigg}__timeSeriesFrequency= "{freq}",
               s.{bigg}__timeSeriesTimeAggregationFunction= "{agg_func}",
               s.{bigg}__timeSeriesStart = CASE 
                   WHEN s.{bigg}__timeSeriesStart < 
                    datetime("{convert(dt_ini).to_pydatetime().isoformat()}") 
                       THEN s.{bigg}__timeSeriesStart
                       ELSE datetime("{convert(dt_ini).to_pydatetime().isoformat()}") 
                   END,
               s.{bigg}__timeSeriesEnd = CASE 
                   WHEN s.{bigg}__timeSeriesEnd >
                    datetime("{convert(dt_end).to_pydatetime().isoformat()}") 
                       THEN s.{bigg}__timeSeriesEnd
                       ELSE datetime("{convert(dt_end).to_pydatetime().isoformat()}")
                   END  
           return s
       """)


def create_sensor(session, device_uri, sensor_uri, unit_uri, property_uri, estimation_method_uri, measurement_uri,
                  is_regular, is_cumulative, is_on_change, freq, agg_func, dt_ini, dt_end, ns_mappings):
    create_timeseries(session=session, ts_uri=sensor_uri, property_uri=property_uri,
                      estimation_method_uri=estimation_method_uri, is_regular=is_regular, is_cumulative=is_cumulative,
                      is_on_change=is_on_change, freq=freq, agg_func=agg_func, dt_ini=dt_ini, dt_end=dt_end,
                      ns_mappings=ns_mappings)

    bigg = ns_mappings['bigg']
    session.run(f"""
        MATCH (device {{uri:"{device_uri}"}})
        MATCH (msu: {bigg}__MeasurementUnit {{uri:"{unit_uri}"}})
        MATCH (s {{uri:"{sensor_uri}"}})   
        MERGE (s)<-[:{bigg}__hasSensor]-(device)
        MERGE (ms: {bigg}__Measurement:Resource:{bigg}__TimeSeriesPoint{{uri: "{measurement_uri}"}})
        Merge(s)-[:{bigg}__hasMeasurementUnit]->(msu)
        Merge(s)-[:{bigg}__hasMeasurement]->(ms)
        SET
            s : {bigg}__Sensor
        return s
    """)


def create_KPI(session, calculation_item_uri, kpi_uri_assesment, unit_uri, property_uri, estimation_method_uri, measurement_uri,
               kpi_uri, is_regular, is_cumulative, is_on_change, freq, agg_func, dt_ini, dt_end, ns_mappings):
    create_timeseries(session=session, ts_uri=kpi_uri_assesment, property_uri=property_uri,
                      estimation_method_uri=estimation_method_uri, is_regular=is_regular, is_cumulative=is_cumulative,
                      is_on_change=is_on_change, freq=freq, agg_func=agg_func, dt_ini=dt_ini, dt_end=dt_end,
                      ns_mappings=ns_mappings)

    bigg = ns_mappings['bigg']
    session.run(f"""
        MATCH (calculation_item {{uri:"{calculation_item_uri}"}})
        MATCH (msu: {bigg}__hasKPIUnit {{uri:"{unit_uri}"}})
        MATCH (s {{uri:"{kpi_uri_assesment}"}})   
        Merge (kpi:Resource:{bigg}__KeyPerformanceIndicator{{uri:"{kpi_uri}"}})   
        MERGE (s)<-[:{bigg}__assessesSingleKPI]-(calculation_item)
        MERGE (ms: {bigg}__SingleKPIAssessmentPoint:Resource:{bigg}__TimeSeriesPoint{{uri: "{measurement_uri}"}})
        Merge(s)-[:{bigg}__hasKPIUnit]->(msu)
        Merge(s)-[:{bigg}__hasSingleKPIPoint]->(ms)
        Merge(s)-[:bigg__quantifiesKPI]->(kpi)
        SET
            s : {bigg}__SingleKPIAssessment
            s : {bigg}__KPIAssessment
        return s
    """)

def create_tariff(session, tariff_dict, data_source, ns_mappings):
    bigg = ns_mappings['bigg']
    tariff_dict = {f"{bigg}__{k}" if k != "uri" else k: v for k, v in tariff_dict.items()}
    session.run(f"""
        MATCH(d:SimpleTariffSource) WHERE id(d)={data_source}
        CREATE(tariff:{bigg}__Tariff:Resource{{ {",".join([f"{k}:'{v}'" for k,v in tariff_dict.items()])} }}) 
        MERGE(tariff)-[:{bigg}__importedFromSource]->(d)
        return tariff
    """)


def create_tariff_component(session, tariff_component_uri, property_uri, estimation_method_uri, is_regular,
                            is_cumulative, is_on_change, freq, agg_func, dt_ini, dt_end, measurement_uri, tariff_uri,
                            priced_property, unit_uri, currency_unit, ns_mappings):
    create_timeseries(session=session, ts_uri=tariff_component_uri, property_uri=property_uri,
                      estimation_method_uri=estimation_method_uri, is_regular=is_regular, is_cumulative=is_cumulative,
                      is_on_change=is_on_change, freq=freq, agg_func=agg_func, dt_ini=dt_ini, dt_end=dt_end,
                      ns_mappings=ns_mappings)

    bigg = ns_mappings['bigg']

    session.run(f"""
    MATCH (tariff: {bigg}__Tariff {{uri:"{tariff_uri}"}})
    MATCH (mes_prop: {bigg}__MeasuredProperty {{uri:"{priced_property}"}})
    MATCH (cur_unit: {bigg}__MeasurementUnit {{uri:"{currency_unit}"}})
    MATCH (prop_unit: {bigg}__MeasurementUnit {{uri:"{unit_uri}"}})
    MATCH (tc {{uri:"{tariff_component_uri}"}})   
    MERGE (tc)<-[:{bigg}__hasTariffComponentList]-(tariff)
    Merge(tc)-[:{bigg}__hasTariffCurrencyUnit]->(cur_unit)
    Merge(tc)-[:{bigg}__hasTariffMeasuredUnit]->(prop_unit)
    Merge(tc)-[:{bigg}__hasTariffMeasuredProperty]->(mes_prop)
    Merge(ms: {bigg}__TariffComponentPoint:Resource:{bigg}__TimeSeriesPoint{{uri: "{measurement_uri}"}})
    Merge(tc)-[:{bigg}__hasTariffComponentPoint]->(ms)
    SET
        tc : {bigg}__TariffComponentList
    return tc""")


def create_co2_component(session, co2_factor_list_uri, property_uri, estimation_method_uri, is_regular,
                         is_cumulative, is_on_change, freq, agg_func, dt_ini, dt_end, measurement_uri, co2_uri,
                         related_prop, related_unit, unit, ns_mappings):
    create_timeseries(session=session, ts_uri=co2_factor_list_uri, property_uri=property_uri,
                      estimation_method_uri=estimation_method_uri, is_regular=is_regular, is_cumulative=is_cumulative,
                      is_on_change=is_on_change, freq=freq, agg_func=agg_func, dt_ini=dt_ini, dt_end=dt_end,
                      ns_mappings=ns_mappings)
    bigg = ns_mappings['bigg']
    session.run(f"""
    MATCH (co2: {bigg}__CO2EmissionsFactor {{uri:"{co2_uri}"}})
    MATCH (mes_prop: {bigg}__MeasuredProperty {{uri:"{related_prop}"}})
    MATCH (unit: {bigg}__MeasurementUnit {{uri:"{unit}"}})
    MATCH (prop_unit: {bigg}__MeasurementUnit {{uri:"{related_unit}"}})
    MATCH (tc {{uri:"{co2_factor_list_uri}"}})   
    MERGE (tc)<-[:{bigg}__hasCO2EmissionsFactorList]-(co2)
    Merge(tc)-[:{bigg}__hasCO2MeasuredUnit]->(unit)
    Merge(tc)-[:{bigg}__hasCO2RelatedMeasuredUnit]->(prop_unit)
    Merge(tc)-[:{bigg}__hasCO2RelatedMeasuredProperty]->(mes_prop)
    Merge(ms: {bigg}__CO2EmissionsPoint:Resource:{bigg}__TimeSeriesPoint{{uri: "{measurement_uri}"}})
    Merge(tc)-[:{bigg}__hasCO2EmissionsFactorValue]->(ms)
    SET
        tc : {bigg}__CO2EmissionsFactorList
    return tc""")


def create_simple_sensor(session, device_uri, sensor_uri, estimation_method_uri,
                         measurement_uri,
                         is_regular, is_cumulative, is_on_change, freq, agg_func, dt_ini, dt_end, ns_mappings):
    bigg = ns_mappings['bigg']

    def convert(tz):
        if not tz.tz:
            tz = tz.tz_localize("UTC")
        if "UTC" != tz.tz.tzname(tz):
            tz = tz.tz_convert("UTC")
        return tz

    session.run(f"""
        MATCH (device: {bigg}__Device {{uri:"{device_uri}"}})
        MATCH (se: {bigg}__SensorEstimationMethod {{uri:"{estimation_method_uri}"}})   
        MERGE (s: {bigg}__Sensor:Resource {{
            uri: "{sensor_uri}"
        }})<-[:{bigg}__hasSensor]-(device)
        Merge(s)-[:{bigg}__hasMeasurementUnit]->(msu)
        Merge(s)-[:{bigg}__hasMeasuredProperty]->(mp)
        Merge(s)-[:{bigg}__hasSensorEstimationMethod]->(se)        
        Merge(s)-[:{bigg}__hasMeasurement]->(ms: {bigg}__Measurement{{uri: "{measurement_uri}"}})
        SET
            s.{bigg}__sensorIsCumulative= {is_cumulative},
            s.{bigg}__sensorIsRegular= {is_regular},
            s.{bigg}__sensorIsOnChange= {is_on_change},
            s.{bigg}__sensorFrequency= "{freq}",
            s.{bigg}__sensorTimeAggregationFunction= "{agg_func}",
            s.{bigg}__sensorStart = CASE 
                WHEN s.{bigg}__sensorStart < 
                 datetime("{convert(dt_ini).to_pydatetime().isoformat()}") 
                    THEN s.{bigg}__sensorStart 
                    ELSE datetime("{convert(dt_ini).to_pydatetime().isoformat()}") 
                END,
            s.{bigg}__sensorEnd = CASE 
                WHEN s.{bigg}__sensorEnd >
                 datetime("{convert(dt_end).to_pydatetime().isoformat()}") 
                    THEN s.{bigg}__sensorEnd
                    ELSE datetime("{convert(dt_end).to_pydatetime().isoformat()}") 
                END  
        return s
    """)
