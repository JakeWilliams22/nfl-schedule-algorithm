import csv
import pandas as pd
import math
import schedule as schedule
from datetime import *



#92 is highest
#-68 is lowest
#92 - -68 = 160
#5 Levels of Difficulty
#160/5=32
#Level 1 = -68 to -36
#Level 2 = -35 to -4
#Level 3 = -3 to 28
#Level 4 = 29 to 62
#Level 5 = 62+

level1 = [] #Easiest
level2 = []
level3 = []
level4 = []
level5 = [] #Hardest


#This function sorts the teams into levels of difficulty as described above. Toughest team is a level5 while the easiest team is a level1
def setTeamDifficulty(dataset):
    data = pd.read_csv(dataset, error_bad_lines=False)
    for i in range(0,len(data['W/L Difference'])):
        if(data['W/L Difference'][i] >= -68 and data['W/L Difference'][i] <= -36):
            level1.append(data[i:i + 1])
            data["Level"][i] = 1
        elif(data['W/L Difference'][i] >= -35 and data['W/L Difference'][i] <= -4):
            level2.append(data[i:i + 1])
            data["Level"][i] = 2
        elif(data['W/L Difference'][i] >= -3 and data['W/L Difference'][i] <= 28):
            level3.append(data[i:i + 1])
            data["Level"][i] = 3
        elif(data['W/L Difference'][i] >= 29 and data['W/L Difference'][i] <= 62):
            level4.append(data[i:i + 1])
            data["Level"][i] = 4
        elif(data['W/L Difference'][i] >= 62):
            level5.append(data[i:i + 1])
            data["Level"][i] = 5
        data.to_csv('NFL .csv', index=False)


#This function takes in a team's schedule in the form of a csv file and calculate the average level of difficulty (1-5)
#FUNCTION STILL NEEDS TO BE LINKED TO RANDOM SCHEDULE GENERATOR ALGORITHM
def calculateScheduleDifficulty(schedule):
    data = pd.read_csv(schedule)
    score = 0
    for i in range(0,len(data)):
        score += data['Level'][i]
    average = score/len(data)
    return(average)

#This function calculate the distance (in kilometers) between 2 teams
def calculateDist(dataset, team1Index, team2Index):
    data = pd.read_csv(dataset)
    team1Lat = math.radians(data['Latt'][team1Index])
    team2Lat = math.radians(data['Latt'][team2Index])
    team1Long = math.radians(data['Long'][team1Index])
    team2Long = math.radians(data['Long'][team2Index])
    dlon = team2Long - team1Long
    dlat = team2Lat - team1Lat
    a = ((math.sin(dlat/2)) * (math.sin(dlat/2))) + math.cos(team1Lat) * math.cos(team2Lat) * ((math.sin(dlon/2)) * (math.sin(dlon/2)))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    dist = 6373 * c
    return(dist)

#This function calculates the average distance of travel of a team's schedule
def calculateScheduleTravelDistance(team):
    data = pd.read_csv(team)
    totalDist = 0
    for i in range(0,len(data)):
        totalDist += data['Distance'][i]
    averageDist = totalDist/len(data)
    return(averageDist)


###############


setTeamDifficulty('NFL .csv')
game_days = schedule.generate_game_days(datetime(2018, 10, 6))
sched = schedule.generate_random_schedule(game_days, schedule.nfl_teams)
print(sched)