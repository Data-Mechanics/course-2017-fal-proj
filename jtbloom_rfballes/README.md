# CS 591 Fall 2017 Project #1: Data Retrieval, Storage, Provenance, and Transformations 
Jake Bloomfeld (jtbloom@bu.edu) and Ricardo Ballesteros (rfballes@bu.edu)
## Project Idea: Sustainability and Transportation in Boston
## Potential Question: What part of Boston is the most "green"?

### Dataset #1: Electric Vehicle Charging Stations (Mass DOT)
##### Website URL: http://geo-massdot.opendata.arcgis.com/datasets/electric-vehicle-charging-stations/data
##### JSON URL: https://opendata.arcgis.com/datasets/ed1c6fb748a646ac83b210985e1069b5_0.geojson
* Important info: station name, address, longitude and latitude, city
  
### Dataset #2: Hubway Station Locations (Boston OpenDataSoft)
#### Website URL: https://boston.opendatasoft.com/explore/dataset/hubway-station-locations/
#### JSON URL: https://boston.opendatasoft.com/explore/dataset/hubway-station-locations/download/?format=geojson&timezone=America/New_York
* Important info: station name, longitude and latitude, municipality, # of docks

### Dataset #3: Existing Bike Network (Analyze Boston)
#### Website URL: https://data.boston.gov/dataset/existing-bike-network
#### JSON URL: http://bostonopendata-boston.opendata.arcgis.com/datasets/d02c9d2003af455fbc37f550cc53d3a4_0.geojson
* Important info: geo point, geo shape, street name
  
### Dataset #4: Boston Neighborhoods (Boston OpenDataSoft)
#### Website URL: https://boston.opendatasoft.com/explore/dataset/boston-neighborhoods/
#### JSON URL: https://boston.opendatasoft.com/explore/dataset/boston-neighborhoods/download/?format=geojson&timezone=America/New_York
* Important info: geo point, geo shape, acres, square miles, neighborhood #

### Dataset #5: Hubway Trip History (Hubway)
#### Website URL: https://www.thehubway.com/system-data
#### JSON URL: http://datamechanics.io/data/jt_rf_pr1/hubway_trip_history.json
* Important info: start station name, start station coordinates, end station name, end station coordinates, start time, stop time

### Narrative
For Project  #1, we picked data sets that revolved around a common theme: sustainability and transportation in Boston. Although at this state we don’t know what specific problem we want to solve, we went ahead to search for data sets that could potentially lead us in the right direction. The data sets we chose are:

* Electrical Vehicle Charging Stations 
* Hubway Station Locations
* Existing Bike Network
* Boston Neighborhoods
* Hubway Trip History

The Electrical Vehicle Charging Stations dataset gives us the names of the stations along with their addresses and geographical coordinate points. The Hubway Station Locations dataset is pretty similar, as it also gives us the names of the stations, their addresses, geographical coordinate points, along with the number of bike docks. The Bike Network dataset gives us a visual representation of bike paths in Boston. Likewise, the Boston Neighborhoods dataset gives usa visual representation of the different neighborhoods within Boston, which could be used to filter data based on neighborhood. Lastly, the Hubway Trip History dataset includes information about trip starting and ending locations, when the trip occured, and duration. We believe that with the right tools, algorithms, and creativity, these datasets can be combined to create a very interesting and informative project.

### Transformations
#### Transformation 1:
For the first transformation, we wanted to modify and clean up the Electric Vehicle Charging Station dataset. This dataset gives us all electric vehicle charging stations within the whole state of MA, but for the purpose of this project, we wanted to narrow them down to only include the stations in Boston. We performed a selection to filter the data, thus, retreiving the stations where the city was equal to 'Boston'. Once the dataset was narrowed down to just Boston stations, we wanted to clean up the dataset and remove any data that we thought was extraneous. The only other fields we wanted to include were 'Station Name', 'Address', 'Longtitude', and 'Latitude'. After extracting those fields, we inserted the new dataset into a dictionary, which was then inserted into a new MongoDB collection.

Transformation file: boston_charging_stations.py

#### Transformation 2 & 3:
This two trasformations are similar in that they are both the derived from the Hubway trip history. The final results tell us the number of (1)incoming trips to every hubway station in the month of january 2015 and (2) outgoing trips of every hubway station in the month of january 2015. The results were obtained by selecting, projecting into a tuple list, and then aggregating by countitng the number of bikes that either started or finished a trip at a certain station. 

Files: outgoing_trips.py and incoming_trips.py

 
 