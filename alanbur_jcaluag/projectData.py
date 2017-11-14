import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class projectData(dml.Algorithm):
    '''
    Class for projecting out the 3 data sets listed in reads
    For each one load in the dataset(overriding the previous one) do appropriate projection and write to file
    '''
    contributor = 'alanbur_jcaluag'
    reads = ['alanbur_jcaluag.trafficSignal', 'alanbur_jcaluag.mbta', 'alanbur_jcaluag.hubway']

    writes = ['alanbur_jcaluag.trafficSignalProjected','alanbur_jcaluag.mbtaProjected', 'alanbur_jcaluag.hubwayProjected']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('alanbur_jcaluag', 'alanbur_jcaluag')

        DSet=[]

        collection=repo['alanbur_jcaluag.trafficSignal'].find()

        DSet=[
            {'Dataset': 'Traffic Signals',
                'Location':item['properties']['Location'],
             'Latitude': item['geometry']['coordinates'][0],
             'Longitude': item['geometry']['coordinates'][1]}
              for item in collection
        ]
        repo.dropCollection("trafficSignalProjected")
        repo.createCollection("trafficSignalProjected")
        repo['alanbur_jcaluag.trafficSignalProjected'].insert_many(DSet)
        repo['alanbur_jcaluag.trafficSignalProjected'].metadata({'complete':True})
        print(repo['alanbur_jcaluag.trafficSignalProjected'].metadata())
        
        collection=repo['alanbur_jcaluag.hubway'].find()
        DSet=[
            {'DataSet': 'Hubway Stations',
                'Location':item['s'],
                'Latitude': item['la'],
                'Longitude': item['lo']}
              for item in collection
        ]
        repo.dropCollection("hubwayProjected")
        repo.createCollection("hubwayProjected")
        repo['alanbur_jcaluag.hubwayProjected'].insert_many(DSet)
        repo['alanbur_jcaluag.hubwayProjected'].metadata({'complete':True})
        print(repo['alanbur_jcaluag.hubwayProjected'].metadata())
        

        collection=repo['alanbur_jcaluag.mbta'].find()
        DSet=[
           {'Data': 'MBTA Bus Stops',
            'Location':item['stop_name'],
            'Latitude':item['stop_lat'],
             'Longitude':item['stop_lon']}
              for item in collection
        ]
        repo.dropCollection("mbtaProjected")
        repo.createCollection("mbtaProjected")
        repo['alanbur_jcaluag.mbtaProjected'].insert_many(DSet)
        repo['alanbur_jcaluag.mbtaProjected'].metadata({'complete':True})
        print(repo['alanbur_jcaluag.mbtaProjected'].metadata())



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
        repo.authenticate('alanbur_jcaluag', 'alanbur_jcaluag')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        
        this_script = doc.agent('alg:alanbur_jcaluag#projectData', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:trafficSignal', {'prov:label':'Traffic Signal Data', prov.model.PROV_TYPE:'ont:DataSet'})
        resource2 = doc.entity('dat:mbta', {'prov:label':'MBTA Stop Data', prov.model.PROV_TYPE:'ont:DataSet'})
        resource3 = doc.entity('dat:hubway', {'prov:label':'Hubway Stop Data', prov.model.PROV_TYPE:'ont:DataSet'})

        get_filter = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_filter, this_script)
        doc.usage(get_filter, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'
                  }
                  )
        doc.usage(get_filter, resource2, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'
                  }
                  )
        doc.usage(get_filter, resource3, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'
                  }
                  )
        projected1 = doc.entity('dat:alanbur_jcaluag#trafficSignalProjected', {prov.model.PROV_LABEL:'Filtered Traffic Data', prov.model.PROV_TYPE:'ont:DataSet'})
        projected2 = doc.entity('dat:alanbur_jcaluag#mbtaProjected', {prov.model.PROV_LABEL:'Filtered Traffic Data', prov.model.PROV_TYPE:'ont:DataSet'})
        projected3 = doc.entity('dat:alanbur_jcaluag#hubwayProjected', {prov.model.PROV_LABEL:'Filtered Traffic Data', prov.model.PROV_TYPE:'ont:DataSet'})
        

        doc.wasAttributedTo(projected1, this_script)
        doc.wasGeneratedBy(projected1, get_filter, endTime)
        doc.wasDerivedFrom(projected1, resource, get_filter, get_filter, get_filter)

        doc.wasAttributedTo(projected2, this_script)
        doc.wasGeneratedBy(projected2, get_filter, endTime)
        doc.wasDerivedFrom(projected2, resource2, get_filter, get_filter, get_filter)

        doc.wasAttributedTo(projected3, this_script)
        doc.wasGeneratedBy(projected3, get_filter, endTime)
        doc.wasDerivedFrom(projected3, resource3, get_filter, get_filter, get_filter)

        repo.logout()
                  
        return doc
    
    
#projectData.execute()