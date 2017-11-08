
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class permit(dml.Algorithm):
    contributor = 'lc546_jofranco'
    reads = []
    writes = ['lc546_jofranco.permit']
    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate("lc546_jofranco", "lc546_jofranco")
        url = 'https://data.cityofboston.gov/resource/fdxy-gydq.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys= True, indent = 2)
        repo.dropCollection("permit")
        repo.createCollection("permit")
        repo["lc546_jofranco.permit"].insert_many(r)
        repo["lc546_jofranco.permit"].metadata({'complete':True})
        print(repo["lc546_jofranco.permit"].metadata())
        repo.logout()
        endTime = datetime.datetime.now()
        return {"start":startTime, "end":endTime}
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate("lc546_jofranco", "lc546_jofranco")
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')
        this_script = doc.agent('alg:lc546_jofranco#retrievedata', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:xgbq-327x', {'prov:label':'permit', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_permitinfo = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime, {prov.model.PROV_LABEL:'permit', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAssociatedWith(get_permitinfo, this_script)
        doc.usage(get_permitinfo, resource, startTime)
        Permitinfo = doc.entity('dat:lc546_jofranco#permitinfo', {prov.model.PROV_LABEL:'restaurant permit', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(Permitinfo, this_script)
        doc.wasGeneratedBy(Permitinfo, get_permitinfo, endTime)
        doc.wasDerivedFrom(Permitinfo, resource, get_permitinfo, get_permitinfo, get_permitinfo)
        return doc



permit.execute()
doc = permit.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

