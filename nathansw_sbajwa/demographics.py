import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import os 

class demographics(dml.Algorithm):

	contributor = 'nathansw_sbajwa'
	reads = []
	writes = ['nathansw_sbajwa.race', 'nathansw_sbajwa.householdincome', 'nathansw_sbajwa.povertyrates', 'nathansw_sbajwa.commuting']

	@staticmethod
	def execute(trial = False):

		startTime = datetime.datetime.now()

		# open db client and authenticate
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('nathansw_sbajwa','nathansw_sbajwa')

		# opens 'Race.json' file from datamechanics.io
		# and inserts it into repo collection 'nathansw_sbajwa.race'

		url = 'http://datamechanics.io/data/nathansw_sbajwa/Race.json'
		response = urllib.request.urlopen(url).read().decode("utf-8")
		r = json.loads(response)
		s = json.dumps(r, indent=4)
		repo.dropCollection("race")
		repo.createCollection("race")
		repo['nathansw_sbajwa.race'].insert_one(r)

		# opens 'MeansOfCommuting.json' file from datamechanics.io
		# and inserts it into repo collection 'nathansw_sbajwa.commuting'

		url = 'http://datamechanics.io/data/nathansw_sbajwa/MeansOfCommuting.json'
		response = urllib.request.urlopen(url).read().decode("utf-8")
		r = json.loads(response)				
		s = json.dumps(r, indent=4)
		repo.dropCollection("commuting")
		repo.createCollection("commuting")
		repo['nathansw_sbajwa.commuting'].insert_one(r)

		# opens 'PovertyRates.json' file from datamechanics.io
		# and inserts it into repo collection 'nathansw_sbajwa.povertyrates'

		url = 'http://datamechanics.io/data/nathansw_sbajwa/PovertyRates.json'
		response = urllib.request.urlopen(url).read().decode("utf-8")
		r = json.loads(response)
		s = json.dumps(r, indent=4)
		repo.dropCollection("povertyrates")
		repo.createCollection("povertyrates")
		repo['nathansw_sbajwa.povertyrates'].insert_one(r)

		# opens 'HouseholdIncome.json' file from datamechanics.io
		# and inserts it into repo collection 'nathansw_sbajwa.householdincome'

		url = 'http://datamechanics.io/data/nathansw_sbajwa/HouseholdIncome.json'
		response = urllib.request.urlopen(url).read().decode("utf-8")
		r = json.loads(response)

		## removes $ from all of the nested keys within the JSON file (char forbidden by mongodb)
		for town in r.keys():
			# Preps variables to alter dict with
			toReplace = {}
			toDelete = []
			for old_key in r[town]:
    			# ex: '$25,000-34,999' -> '25,000-34,999'
				new_key = old_key.replace('$', '')
        		# only continue if the original key had a $ that needed to be removed
				if new_key != old_key:
					# puts new key in seperate dict
					toReplace[new_key] = r[town][old_key]
					# adds old key to list of keys to be deleted
					toDelete += [old_key]
			# merges two dicts i.e. r[town] contains both old and new keys ($ and no $)
			r[town].update(toReplace)
			# deletes old keys from r[town] leaving only kys with no $
			for key in toDelete:
				del r[town][key]

		s = json.dumps(r, indent=4)
		repo.dropCollection("householdincome")
		repo.createCollection("householdincome")
		repo['nathansw_sbajwa.householdincome'].insert_one(r)

		# logs out of db
		repo.logout()

		endTime = datetime.datetime.now()

		return {"start": startTime, "end": endTime}

	@staticmethod
	def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):

		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate("nathansw_sbajwa","nathansw_sbajwa")
		doc.add_namespace('alg', 'http://datamechanics.io/algorithm/sbajwa_nathansw/') # The scripts in / format.
		doc.add_namespace('dat', 'http://datamechanics.io/data/sbajwa_nathansw/') # The data sets in / format.
		doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
		doc.add_namespace('log', 'http://datamechanics.io/log#') # The event log.

		doc.add_namespace('race', 'http://datamechanics.io/data/nathansw_sbajwa/') 
		doc.add_namespace('povertyrates', 'http://datamechanics.io/data/nathansw_sbajwa/')
		doc.add_namespace('householdincome', 'http://datamechanics.io/data/nathansw_sbajwa/')
		doc.add_namespace('commuting', 'http://datamechanics.io/data/nathansw_sbajwa/')

		this_script = doc.agent('alg:nathansw_sbajwa#demographics', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})

		get_race = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_povertyrates = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_householdincome = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_commuting = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

		resource1 = doc.entity('race: Race.json', {'prov:label':'Race by Neighborhood', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
		resource2 = doc.entity('povertyrates: PovertyRates.json', {'prov:label':'Poverty Rates by Neighborhood', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
		resource3 = doc.entity('householdincome: HouseholdIncome.json', {'prov:label':'Household Income by Neighborhood', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
		resource4 = doc.entity('commuting: MeansOfCommuting.json', {'prov:label':'Means of Commuting by Neighborhood', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})

		doc.wasAssociatedWith(get_race, this_script)
		doc.usage(get_race, resource1, startTime, None,{prov.model.PROV_TYPE:'ont:Retrieval'})

		doc.wasAssociatedWith(get_povertyrates, this_script)
		doc.usage(get_povertyrates, resource2, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})

		doc.wasAssociatedWith(get_householdincome, this_script)
		doc.usage(get_householdincome, resource3, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})

		doc.wasAssociatedWith(get_commuting, this_script)
		doc.usage(get_commuting, resource4, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})

		race = doc.entity('dat:nathansw_sbajwa#race', {prov.model.PROV_LABEL:'Race by Neighborhood', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(race, this_script)
		doc.wasGeneratedBy(race, get_race, endTime)
		doc.wasDerivedFrom(race, resource1, get_race, get_race, get_race)			

		povertyrates = doc.entity('dat:nathansw_sbajwa#povertyrates', {prov.model.PROV_LABEL:'Poverty by Neighborhood', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(povertyrates, this_script)
		doc.wasGeneratedBy(povertyrates, get_povertyrates, endTime)
		doc.wasDerivedFrom(povertyrates, resource2, get_povertyrates, get_povertyrates, get_povertyrates)		

		householdincome = doc.entity('dat:nathansw_sbajwa#householdincome', {prov.model.PROV_LABEL:'Household Income by Neighborhood', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(householdincome, this_script)
		doc.wasGeneratedBy(householdincome, get_householdincome, endTime)
		doc.wasDerivedFrom(householdincome, resource3, get_householdincome, get_householdincome, get_householdincome)		

		commuting = doc.entity('dat:nathansw_sbajwa#commuting', {prov.model.PROV_LABEL:'Means of Commuting by Neighborhood', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(commuting, this_script)
		doc.wasGeneratedBy(commuting, get_commuting, endTime)
		doc.wasDerivedFrom(commuting, resource4, get_commuting, get_commuting, get_commuting)		

		repo.logout()

		return doc

# demographics.execute()
# doc = demographics.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))