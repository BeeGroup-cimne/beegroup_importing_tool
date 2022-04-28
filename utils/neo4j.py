def get_devices_from_datasource(session, user, device_id, source):
    device_neo = session.run(f"""
                MATCH (ns0__Organization{{ns0__userId:'{user}'}})-[:ns0__hasSubOrganization*0..]->(o:ns0__Organization)-
                [:ns0__hasSource]->(s:DatadisSource)<-[:ns0__importedFromSource]-(d)
                WHERE d.source = "DatadisSource" AND d.ns0__deviceName = "{device_id}" return d            
                """)
    return device_neo


def create_sensor(session, device_uri, sensor_uri, unit_uri, property_uri, estimation_method_uri, measurement_uri,
                  is_cumulative, is_on_change, freq, agg_func, dt_ini, dt_end):
    session.run(f"""
        MATCH (device: ns0__Device {{uri:"{device_uri}"}})
        MERGE (s: ns0__Sensor {{
            uri: "{sensor_uri}"
        }})<-[:ns0__hasSensor]-(device)
        Merge(s)-[:ns0__hasMeasurementUnit]->(ms: ns0__MeasurementUnit{{
            uri: "{unit_uri}"
        }})
        Merge(s)-[:ns0__hasMeasuredProperty]->(ms: ns0__MeasuredProperty{{
            uri: "{property_uri}"
        }})
        Merge(s)-[:hasSensorEstimationMethod]->(ms: ns0__SensorEstimationMethod{{
            uri: "{estimation_method_uri}"
        }})        
        Merge(s)-[:hasMeasurement]->(ms: ns0__Measurement{{
            uri: "{measurement_uri}"
        }})
        SET
            s.ns0__sensorIsCumulative= "{is_cumulative}",
            s.ns0__sensorIsOnChange= "{is_on_change}",
            s.ns0__sensorFrequency= "{freq}",
            s.ns0__sensorTimeAggregationFunction= "{agg_func}",
            s.ns0__sensorStart = CASE 
                WHEN s.ns0__sensorStart < 
                 datetime("{dt_ini.tz_localize("UTC").to_pydatetime().isoformat()}") 
                    THEN s.ns0__sensorStart 
                    ELSE datetime("{dt_ini.tz_localize("UTC").to_pydatetime().isoformat()}") 
                END,
            s.ns0__sensorEnd = CASE 
                WHEN s.ns0__sensorEnd >
                 datetime("{dt_end.tz_localize("UTC").to_pydatetime().isoformat()}") 
                    THEN s.ns0__sensorEnd
                    ELSE datetime("{dt_end.tz_localize("UTC").to_pydatetime().isoformat()}") 
                END  
        return s
    """)
