import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class schools(dml.Algorithm):
    contributor = 'wongi'
    reads = []
    writes = ['wongi.schools']

    @staticmethod
    def execute(trial = False):
        '''Retrieve Boston Public Schools Data from City of Boston .'''
        startTime = datetime.datetime.now()
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('wongi', 'wongi')

        url = 'https://data.cityofboston.gov/resource/492y-i77g.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("schools")
        repo.createCollection("schools")
        repo['wongi.schools'].insert_many(r)
        print('Load public schools')
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
        repo.authenticate('wongi', 'wongi')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:wongi#schools', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:1d9509a8b2fd485d9ad471ba2fdb1f90_0', {'prov:label':'Boston Public School', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_schools = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_schools, this_script)
        doc.usage(get_schools, resource, startTime, None,
                {prov.model.PROV_TYPE:'ont:Retrieval'}
            )

        schools = doc.entity('dat:wongi#schools', {prov.model.PROV_LABEL:'Boston Public Schools ', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(schools, this_script)
        doc.wasGeneratedBy(schools, get_schools, endTime)
        doc.wasDerivedFrom(schools, resource, get_schools, get_schools, get_schools)

        repo.logout()

        return doc

