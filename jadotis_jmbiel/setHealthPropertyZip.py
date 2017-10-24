from urllib.request import urlopen
import json
import dml
import prov.model
import datetime
import uuid
import time
import ssl

"""
Helper Functions courtesy of Andrei Lapets - CS591 BU
"""
from math import sin, cos, sqrt, atan2, radians
import math

# approximate radius of earth in km

def union(R, S):
    return R + S

def difference(R, S):
    return [t for t in R if t not in S]

def intersect(R, S):
    return [t for t in R if t in S]

def project(R, p):
    return [p(t) for t in R]

def select(R, s):
    return [t for t in R if s(t)]
 
def product(R, S):
    return [(t,u) for t in R for u in S]

def aggregate(R, f):
    keys = {r[0] for r in R}
    return [(key, f([v for (k,v) in R if k == key])) for key in keys]


def calculateDist(d1, d2):
    R = 6373.0
    d1 = d1.replace("(", "").replace(")", "")
    d1 = d1.split(",")
    d1 = (float(d1[0]), float(d1[1]))

    d2 = d2.replace("(", "").replace(")", "")
    d2 = d2.split(",")
    d2 = (float(d2[0]), float(d2[1]))

    lat1 = radians(d1[0])
    lon1 = radians(d1[1])
    lat2 = radians(d2[0])
    lon2 = radians(d2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance <= 1


def dist(p, q):
    (x1,y1) = p
    (x2,y2) = q
    return (x1-x2)**2 + (y1-y2)**2

def plus(args):
    p = [0,0]
    for (x,y) in args:
        p[0] += x
        p[1] += y
    return tuple(p)

def scale(p, c):
    (x,y) = p
    return (x/c, y/c)
#End Helpers



class setHealthPropertyZip(dml.Algorithm):
    contributor = 'biel_otis'
    reads = ['biel_otis.HealthInspection', 'biel_otis.PropertyValues', 'biel_otis.ZipCodes']
    writes = ['biel_otis.HealthPropertyZip']

    @staticmethod
    def execute(trial = False):        
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client['biel_otis']
        repo.authenticate('biel_otis', 'biel_otis')
        print("Retrieving Data....")
        HealthInspections = repo['biel_otis.HealthInspection'].find()
        PropertyValues = list(repo['biel_otis.PropertyValues'].find())
        ZipCodes = repo['biel_otis.ZipCodes'].find()
        Zips = ZipCodes.distinct('1')
        print("finished getting data...")
        props = [x for x in PropertyValues if x['owner_mail_zipcode'] in Zips] # Join operation on ZipCodes (had to append leading 0 to zipcode)
        
        props_extract = project(props, lambda x: (x['av_total'], x['location'], x['owner_mail_address'] + " " + x['owner_mail_cs'] + " " + x['owner_mail_zipcode']))
        # returns tuple of form (av_total, location, address)
        
        inspections = [x for x in HealthInspections if x['DESCRIPT'] == 'Eating & Drinking' and x['ViolStatus'] == 'Fail' and x['ZIP'] in Zips]

        inspections_extract = project(inspections, lambda x: (x['businessName'], x['Address'] + " " + x['CITY'] + " " + x['ZIP'], x['Location']))
        # returns tuples of form (businessName, Address, location)
        
        bad_str = "[]\;?><./!@#$%^&*+"
        dist_calc = [(x, y) for x in props_extract for y in inspections_extract if (x[1] not in bad_str and y[2] not in bad_str) and calculateDist(x[1], y[2])]
        near_final_set = [(x[0], 1) for x in dist_calc]
        final_set = aggregate(near_final_set, sum)
        #Now we have Income(value, 1) figure out the sum
        mongo_input = [{str(x[0]).replace('.','_'): x[1]} for x in final_set]
        print("Finished Transformations...")
        repo.dropCollection("HealthPropertyZip")
        repo.createCollection("HealthPropertyZip")
        repo['biel_otis.HealthPropertyZip'].insert_many(mongo_input)
        repo['biel_otis.HealthPropertyZip'].metadata({'complete':True})
        print(repo['biel_otis.HealthPropertyZip'].metadata())
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
        repo = client['biel_otis']
        repo.authenticate('biel_otis', 'biel_otis')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:biel_otis#setHealthPropertyZip', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        #resource = doc.entity('health:458/2be/4582bec6-2b4f-4f9e-bc55-cbaa73117f4c', {'prov:label':'Health Inspections in City of Boston', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        health = doc.entity('dat:biel_otis#health', {prov.model.PROV_LABEL:'Health Inspections in City of Boston', prov.model.PROV_TYPE:'ont:DataSet'})
        props = doc.entity('dat:biel_otis#propertys', {prov.model.PROV_LABEL:'Dataset of property values in the city of Boston', prov.model.PROV_TYPE:'ont:Dataset'})
        zips = doc.entity('dat:biel_otis#zipcodes', {prov.model.PROV_LABEL:'Dataset containing zipcode information in the city of Boston', prov.model.PROV_TYPE:'ont:DataSet'})
        props_failed_HI = doc.entity('dat:biel_otis#prop_vals_and_failed_health_inspects', {prov.model.PROV_LABEL:'Dataset containing key value pairs where the key is the value of some property, and the value is the number of restaurants that failed health inspections within 1 square mile.', prov.model.PROV_TYPE:'ont:DataSet'})


        gen_HealthPropZip = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(gen_HealthPropZip, this_script)
        
        doc.usage(gen_HealthPropZip, health, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Transformation'})
        doc.usage(gen_HealthPropZip, props, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Transformation'})
        doc.usage(gen_HealthPropZip, zips, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Transformation'})
        doc.usage(gen_HealthPropZip, props_failed_HI, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Transformation'})

        doc.wasAttributedTo(props_failed_HI, this_script)
        doc.wasGeneratedBy(props_failed_HI, gen_HealthPropZip, endTime)
        doc.wasDerivedFrom(health, props, zips, gen_HealthPropZip, gen_HealthPropZip, gen_HealthPropZip)
        repo.logout()
        
        return doc

print("Finished SetHealthPropertyZip")

## eof
