import json
import geopy.distance

# Helper function to clean data for one technician into the form below
def cleanTech(raw_tech):
  return {
    "name": raw_tech["properties"]["name"],
    "bearing": raw_tech["properties"]["bearing"],
    "coordinates": raw_tech["geometry"]["coordinates"]
  }

# Helper function to get the data into the most convenient format
# For simplicity, (only keeping tracking of the data we'll need) we want to convert it to
# [{
#   tsecs: num,
#   techs: [
#     {
#       name: string,
#       bearing: num,
#       coordinates: [num, num],  
#     } 
#   ]
# }]
# Note that while we are losing some of the fields from the original data, none of them
# were relevant to the problem at hand, so for the purpose of clarity in this programming
# assignment I've decided to remove them
def initializeRelevantData(filename):
  result = []
  with open(filename) as f:
    data = json.load(f)
    for row in data:
      raw_techs = row["features"]
      if len(raw_techs):
        tsecs = raw_techs[0]["properties"]["tsecs"],
        techs = list(map(cleanTech, raw_techs))
        result.append({ "tsecs": tsecs[0], "techs": techs })
  return result

# Given two technicians of the form 
# {
#   name: string,
#   bearing: num,
#   coordinates: [num, num],  
# }
# returns the distance between them in meters 
# Note: Uses the geopy library to help with long/lat calculations
def getDistBetweenTechs(t1, t2):
  return geopy.distance.distance(
    (t1["coordinates"][1], t1["coordinates"][0]), 
    (t2["coordinates"][1], t2["coordinates"][0])
  ).ft

# Given a point in time, calculate a dictionary that has distances between the techs
# Returns a tuple with this array, and a boolean if it contains two techs within the flag_dist of each other
def getTotalDists(techs, flag_dist=1000):
  result = {}
  flag = False
  for ix in range(len(techs)):
    t1 = techs[ix]
    result[t1["name"]] = {}
    for jx in range(len(techs)):
      # Note: we choose to include all jx here so that this distance dictionary is symmetric
      t2 = techs[jx]
      d = getDistBetweenTechs(t1, t2)
      if d < flag_dist and ix != jx: # Make sure we don't count distance between tech and themself as too close
        flag = True
      result[t1["name"]][t2["name"]] = getDistBetweenTechs(t1, t2)
  return (result, flag)

def main():
  data = initializeRelevantData("api_technician_response_data.json")
  # final_data will map points in time for every tsec to an object of the form
  # {
  #   flagged: boolean,
  #   distMap: {}, a dictionary mapping tech names to the distance between them
  # }
  final_data = {}
  # This way, final_data[tsecs][name1][name2] will represent the distance between name1 and name2 at time tsecs
  for row in data:
    (distMap, flagged) = getTotalDists(row["techs"])
    final_data[row["tsecs"]] = {
      "distMap": distMap,
      "flagged": flagged
    }

"""
TAKE THIS FURTHER
To take this further and predict when technicians are going to intersect, I would first
use the coordinate data to try and extrapolate speed of each technician at each time.
This would simply be an estimate of the amount of distance they covered since the last interval,
and it would be used to estimate where the would be at the next interval (or ten intervals from now).

Then, at each time I would use the estimate of the technicians speed and measurement of its bearing
to predict where that technician would be in a certain amount of time (likely the same amount of time
as is one interval). Once this is done for all the technicians, I would be able to run a very similar
algorithm to the one above to see if any of the technicians are predicted to be within a certain
radius of each other, and could make adjustments then as needed.

To make the bearing specific calculations I would likely use a function from the geopy library, working
in lat/long coordinates until the very end when I want to convert into feet.
"""

if __name__ == "__main__":
   main()