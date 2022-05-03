import settings

bigg = settings.namespace_mappings['bigg']


def get_devices_from_datasource(session, user, device_id, source):
    device_neo = session.run(f"""
                MATCH ({bigg}__Organization{{userID:'{user}'}})-[:{bigg}__hasSubOrganization*0..]->(o:{bigg}__Organization)-
                [:hasSource]->(s:{source})<-[:importedFromSource]-(d)
                WHERE d.source = "{source}" AND d.{bigg}__deviceName = ["{device_id}"] return d            
                """)
    return device_neo


def create_sensor(session, device_uri, sensor_uri, unit_uri, property_uri, estimation_method_uri, measurement_uri,
                  is_cumulative, is_on_change, freq, agg_func, dt_ini, dt_end):
    session.run(f"""
        MATCH (device: {bigg}__Device {{uri:"{device_uri}"}})
        MATCH (msu: {bigg}__MeasurementUnit {{uri:"{unit_uri}"}})
        MATCH (mp: {bigg}__MeasuredProperty {{uri:"{property_uri}"}})
        MATCH (se: {bigg}__SensorEstimationMethod {{uri:"{estimation_method_uri}"}})   
        MERGE (s: {bigg}__Sensor {{
            uri: "{sensor_uri}"
        }})<-[:{bigg}__hasSensor]-(device)
        Merge(s)-[:{bigg}__hasMeasurementUnit]->(msu)
        Merge(s)-[:{bigg}__hasMeasuredProperty]->(mp)
        Merge(s)-[:{bigg}__hasSensorEstimationMethod]->(se)        
        Merge(s)-[:{bigg}__hasMeasurement]->(ms: {bigg}__Measurement{{uri: "{measurement_uri}"}})
        SET
            s.{bigg}__sensorIsCumulative= "{is_cumulative}",
            s.{bigg}__sensorIsOnChange= "{is_on_change}",
            s.{bigg}__sensorFrequency= "{freq}",
            s.{bigg}__sensorTimeAggregationFunction= "{agg_func}",
            s.{bigg}__sensorStart = CASE 
                WHEN s.{bigg}__sensorStart < 
                 datetime("{dt_ini.tz_localize("UTC").to_pydatetime().isoformat()}") 
                    THEN s.{bigg}__sensorStart 
                    ELSE datetime("{dt_ini.tz_localize("UTC").to_pydatetime().isoformat()}") 
                END,
            s.{bigg}__sensorEnd = CASE 
                WHEN s.{bigg}__sensorEnd >
                 datetime("{dt_end.tz_localize("UTC").to_pydatetime().isoformat()}") 
                    THEN s.{bigg}__sensorEnd
                    ELSE datetime("{dt_end.tz_localize("UTC").to_pydatetime().isoformat()}") 
                END  
        return s
    """)
