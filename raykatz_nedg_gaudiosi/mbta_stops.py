import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import random

from shapely.geometry import shape, Point

class mbta_stops(dml.Algorithm):
    contributor = 'raykatz_nedg_gaudiosi'
    reads = ['raykatz_nedg_gaudiosi.mbta_routes','raykatz_nedg_gaudiosi.zipcode_map']
    writes = ['raykatz_nedg_gaudiosi.mbta_stops']

    @staticmethod
    def execute(trial = False):
        '''Retrieve mbta_stops data from realtime.mbta.com'''
        startTime = datetime.datetime.now()
        trial_zips = ["02116", "02134", "02215"]
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('raykatz_nedg_gaudiosi', 'raykatz_nedg_gaudiosi')
        
        
        
        with open('auth.json') as data_file:    
                data = json.load(data_file)
        
        routes = list(repo.raykatz_nedg_gaudiosi.mbta_routes.find({}))
        
        r = []
        geo_map = list(repo.raykatz_nedg_gaudiosi.zipcode_map.find({}))[0]


        for route in routes:
            if trial and not route["mode_name"] == "Subway":
                continue

            url = "http://realtime.mbta.com/developer/api/v2/stopsbyroute?api_key=" + data["mbta"] + "&route=" + route["route_id"] +  "&format=json"
            response = urllib.request.urlopen(url).read().decode("utf-8")        
            stops = json.loads(response)
            for direction in stops["direction"]:
                for stop in direction["stop"]:
                    s = {}                   
                    s["mode_name"] = route["mode_name"]
                    s["route_id"] = route["route_id"]
                    s["route_name"] = route["route_name"]
                    s["direction"] = direction["direction_name"]
                    s["stop_order"] = stop["stop_order"]
                    s["stop_id"] = stop["stop_id"]
                    s["stop_name"] = stop["stop_name"]
                    s["parent_station"] = stop["parent_station"]
                    s["parent_station_name"] = stop["parent_station_name"]
                    s["stop_lat"] = stop["stop_lat"]
                    s["stop_lon"] = stop["stop_lon"]
                    
                    point = Point(float(s["stop_lon"]),float(s["stop_lat"]))
                    
                    for feature in geo_map["features"]:
                        polygon = shape(feature['geometry'])
                        inside = polygon.contains(point)
                        if polygon.contains(point):
                            zipcode = feature["properties"]["ZIP5"]
                            s["zipcode"] = zipcode
                            break
                    
                    if not "zipcode" in s:
                        continue
                    
                    r.append(s)
        
        s = json.dumps(r, sort_keys=True, indent=2)        
        repo.dropCollection("mbta_stops")
        repo.createCollection("mbta_stops")
        repo['raykatz_nedg_gaudiosi.mbta_stops'].insert_many(r)
        repo['raykatz_nedg_gaudiosi.mbta_stops'].metadata({'complete':True})
        print(repo['raykatz_nedg_gaudiosi.mbta_stops'].metadata())
        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('raykatz_nedg_gaudiosi', 'raykatz_nedg_gaudiosi')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('mbta', 'http://realtime.mbta.com/developer/api/v2/')

        this_script = doc.agent('alg:raykatz_nedg_gaudiosi#proj1', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:raykatz_nedg_gaudiosi#mbta_routes', {'prov:label':'MBTA Routes', prov.model.PROV_TYPE:'ont:DataSet'})
        resource2 = doc.entity('mbta:stopsbyroute', {'prov:label':'MBTA Stops By Route', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
               
        #stopsbyroute?api_key=" + data["mbta"] + "&route=" + route["route_id"] +  "&format=json"
        
        get_mbta_stops = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_mbta_stops, this_script)
        
        doc.usage(get_mbta_stops, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'}
                  )

        doc.usage(get_mbta_stops, resource2, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?api_key=KEY&route=ROUTE&format=json'
                  }
                  )
        
        mbta_stops = doc.entity('dat:raykatz_nedg_gaudiosi#mbta_stops', {prov.model.PROV_LABEL:'MBTA Stops', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(mbta_stops, this_script)
        doc.wasGeneratedBy(mbta_stops, get_mbta_stops, endTime)
        doc.wasDerivedFrom(mbta_stops, resource, get_mbta_stops, get_mbta_stops, get_mbta_stops)
        doc.wasDerivedFrom(mbta_stops, resource2, get_mbta_stops, get_mbta_stops, get_mbta_stops)
        repo.logout()
                  
        return doc
'''
mbta_stops.execute()
doc = mbta_stops.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
## eof
