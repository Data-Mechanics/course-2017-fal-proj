import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class housing_percentages(dml.Algorithm):
    contributor = 'gaudiosi_raykatz'
    reads = ["gaudiosi_raykatz.housing"]
    writes = ['gaudiosi_raykatz.housing_percentages']

    @staticmethod
    def execute(trial = False):
        '''Merge zipcode info'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('gaudiosi_raykatz', 'gaudiosi_raykatz')
       
        
        repo.dropCollection("housing_percentages")
        repo.createCollection("housing_percentages")

        repo.gaudiosi_raykatz.housing.aggregate( [ {"$project":{
                                                "zipcode":1,
                                                "percent_homes_occupied":{"$divide": ["$occupied_housing", "$total_housing"]},
                                                "percent_homes_vacant":{"$divide": ["$vacant_housing", "$total_housing"]},
                                                "percent_homes_built_before_1939":{"$divide": ["$structures_build_before_1939", "$total_structures_built"]},
                                                }},
                                                
                                                {"$out": "gaudiosi_raykatz.housing_percentages"}

        ])
         
        repo['gaudiosi_raykatz.housing_percentages'].metadata({'complete':True})
        print(repo['gaudiosi_raykatz.housing_percentages'].metadata())
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
        repo.authenticate('gaudiosi_raykatz', 'gaudiosi_raykatz')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:gaudiosi_raykatz#proj1', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_demos = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_demos, this_script)
        
        doc.usage(get_demos, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Housing Percentages&$select=occupied,vacant,total,before_1939,total_structs'
                  }
                  )
        
        demos = doc.entity('dat:gaudiosi_raykatz#housing_percentages', {prov.model.PROV_LABEL:'Housing', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(demos, this_script)
        doc.wasGeneratedBy(demos, get_demos, endTime)
        doc.wasDerivedFrom(demos, resource, get_demos, get_demos, get_demos)

        repo.logout()
                  
        return doc
'''
housing_percentages.execute()
doc = housing_percentages.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
## eof
