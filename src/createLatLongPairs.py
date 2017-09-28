# import math
# import csv as csv
# import pandas as pd

# from schedule import nfl_teams

# nfl_data = pd.read_csv("../data/NFL.csv")
# dest = '../data/stadiumDistances.csv'
 
# def travelDistance(data, team1, team2):
    # team1Lat = math.radians(data[data['Team Name'] == team1]['Latt'])
    # team2Lat = math.radians(data[data['Team Name'] == team2]['Latt'])
    # team1Long = math.radians(data[data['Team Name'] == team1]['Long'])
    # team2Long = math.radians(data[data['Team Name'] == team2]['Long'])
    # dlon = team2Long - team1Long
    # dlat = team2Lat - team1Lat
    # a = ((math.sin(dlat/2)) * (math.sin(dlat/2))) + math.cos(team1Lat) * math.cos(team2Lat) * ((math.sin(dlon/2)) * (math.sin(dlon/2)))
    # c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    # dist = 6373 * c #approximate radius of earth
    # return(dist)
    
# def createCSV():
    # with open(dest, 'w') as csvFile:
        # writer = csv.writer(csvFile, delimiter=",")
        # teams = list(nfl_teams)
        # for team1 in teams:
            # for team2 in teams:
                # if team1 == team2:
                    # continue
                # dist = travelDistance(nfl_data, team1, team2)
                # writer.writerow([str(team1), str(team2), str(dist)])
                # writer.writerow([str(team2), str(team1), str(dist)])
# createCSV()            