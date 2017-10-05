import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class roadComplainAgg(dml.Algorithm):
    '''
    Filter the road complain data to get only relevent data.
    Next aggregate data by date and get a list of all complaints on that day through a projection
    '''
    contributor = 'alanbur_jcaluag'
    reads = ['alanbur_jcaluag.roadComplaints']
    writes = ['alanbur_jcaluag.roadComplaintsByDate']
    
    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('alanbur_jcaluag', 'alanbur_jcaluag')
 
        DSet=[]

        collection=repo['alanbur_jcaluag.roadComplaints'].find()
        DSet=[]
        # keys = {r[0] for r in R}
        # [(key, f([v for (k,v) in R if k == key])) for key in keys]
        DSet=[
             
             {
                'Latitude': item['geometry']['coordinates'][0],
                'Longitude': item['geometry']['coordinates'][1],
                'UserType' : item['properties']['USERTYPE'],
                'UserType' : item['properties']['COMMENTS'],
                'Comments':item['properties']['COMMENTS'],
                'Status': item['properties']['STATUS'],
                'Date' : item['properties']['REQUESTDATE'][:item['properties']['REQUESTDATE'].index(':')]
            }
            
              for item in collection
        ]
        DSetByDate=[]
        dates=set()
        for item in DSet:
            dates.add(item['Date'])
        for date in dates:
            [DSetByDate.append({"Date": date,
                "Incidents":[item for item in DSet if item['Date']==date]
                })
            ]
            

        repo.dropCollection("roadComplaintsByDate")
        repo.createCollection("roadComplaintsByDate")
        repo['alanbur_jcaluag.roadComplaintsByDate'].insert_many(DSet)
        repo['alanbur_jcaluag.roadComplaintsByDate'].metadata({'complete':True})
        print(repo['alanbur_jcaluag.roadComplaintsByDate'].metadata())
        
        

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
        
        this_script = doc.agent('alg:alanbur_jcaluag#roadComplainAgg', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:alanbur_jcaluag#roadComplaints', {'prov:label':'Road Complaints', prov.model.PROV_TYPE:'ont:DataSet'})
        get_complaints = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_complaints, this_script)
        doc.usage(get_complaints, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'
                  }
                  )

        roadComplaints = doc.entity('dat:alanbur_jcaluag#roadComplaintsByDate', {prov.model.PROV_LABEL:'Road Complaints by date', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(roadComplaints, this_script)
        doc.wasGeneratedBy(roadComplaints, get_complaints, endTime)
        doc.wasDerivedFrom(roadComplaints, resource, get_complaints, get_complaints, get_complaints)

        repo.logout()
                  
        return doc
# roadComplaints.execute()