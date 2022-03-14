import pandas as pd
import numpy as np
import matplotlib.cbook as cbook
from distribution import getCombinedDistribution

__author__ = "Dr Nancy Retzlaff"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = ["Nancy Retzlaff"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Dr Nancy Retzlaff"
__email__ = "retzlaff@wifa.uni-leipzig.de"
__status__ = "Prototype"

# data is organized in day of the week, date, entries, exits
# In this special case it was distinguished between short visits and long-term parking and the sum of both for each
# exit and entry
# todo add file path
path = 'data/'
driveInAndOut = pd.read_csv(path, sep=",")

mondayIn = []
mondayOut = []
tuesdayIn = []
tuesdayOut = []
wednesdayIn = []
wednesdayOut = []
thursdayIn = []
thursdayOut = []
fridayIn = []
fridayOut = []
saturdayIn = []
saturdayOut = []
sundayIn = []
sundayOut = []

# organize data in weekdays
for i in range(len(driveInAndOut)):
    if driveInAndOut['Wochentag'][i] == 'Montag':
        mondayIn.append(driveInAndOut['Summe Einfahrten'][i])
        mondayOut.append(driveInAndOut['Summe Ausfahrten'][i])
    elif driveInAndOut['Wochentag'][i] == 'Dienstag':
        tuesdayIn.append(driveInAndOut['Summe Einfahrten'][i])
        tuesdayOut.append(driveInAndOut['Summe Ausfahrten'][i])
    elif driveInAndOut['Wochentag'][i] == 'Mittwoch':
        wednesdayIn.append(driveInAndOut['Summe Einfahrten'][i])
        wednesdayOut.append(driveInAndOut['Summe Ausfahrten'][i])
    elif driveInAndOut['Wochentag'][i] == 'Donnerstag':
        thursdayIn.append(driveInAndOut['Summe Einfahrten'][i])
        thursdayOut.append(driveInAndOut['Summe Ausfahrten'][i])
    elif driveInAndOut['Wochentag'][i] == 'Freitag':
        fridayIn.append(driveInAndOut['Summe Einfahrten'][i])
        fridayOut.append(driveInAndOut['Summe Ausfahrten'][i])
    elif driveInAndOut['Wochentag'][i] == 'Samstag':
        saturdayIn.append(driveInAndOut['Summe Einfahrten'][i])
        saturdayOut.append(driveInAndOut['Summe Ausfahrten'][i])
    elif driveInAndOut['Wochentag'][i] == 'Sonntag':
        sundayIn.append(driveInAndOut['Summe Einfahrten'][i])
        sundayOut.append(driveInAndOut['Summe Ausfahrten'][i])

# plot entries and exits separately
week = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
x = range(len(week))

entries = [mondayIn, tuesdayIn, wednesdayIn, thursdayIn, fridayIn, saturdayIn, sundayIn]
exits = [mondayOut, tuesdayOut, wednesdayOut, thursdayOut, fridayOut, saturdayOut, sundayOut]

# plt.boxplot(entries, labels=week)
# plt.title("entries")
# plt.show()
# plt.savefig("plots/weekly_distribution.pdf")

# plt.boxplot(exits, labels=week)
# plt.title("exits")
# plt.show()

statsIn = {}
statsOut = {}

for i in x:
    statsIn[week[i]] = cbook.boxplot_stats(entries[i], labels=week[i][0])[0]
    statsOut[week[i]] = cbook.boxplot_stats(exits[i], labels=week[i][0])[0]
    statsIn[week[i]]['q1'], statsIn[week[i]]['q3'] = np.percentile(entries[i], [20, 80])
    statsOut[week[i]]['q1'], statsOut[week[i]]['q3'] = np.percentile(exits[i], [20, 80])  # change percentiles here.
    # NOTE: when the data is scattered to much whiskers point in the wrong direction, i.e., they point inside the box

# fig, ax = plt.subplots(1, 1)
# Plot boxplots from our computed statistics
# bp = ax.bxp([statsIn['Monday'], statsIn['Tuesday'], statsIn['Wednesday'], statsIn['Thursday'], statsIn['Friday'],
#              statsIn['Saturday'], statsIn['Sunday']], positions=range(7))

# Color the lines in the boxplot blue
# for element in bp.keys():
#     plt.setp(bp[element], color='C0')

# plt.title("Entries, other Percentiles")
# plt.show()

# fig, ax = plt.subplots(1, 1)
# bp = ax.bxp(
#     [statsOut['Monday'], statsOut['Tuesday'], statsOut['Wednesday'], statsOut['Thursday'], statsOut['Friday'],
#      statsOut['Saturday'], statsOut['Sunday']], positions=range(7))

# for element in bp.keys():
#     plt.setp(bp[element], color='C0')

# plt.title("Exits, other Percentiles")
# plt.show()

utilizationPerQuarter, shift = getCombinedDistribution()

deltas = 0
for i in range(len(utilizationPerQuarter)):
    # calculate finite differences a.k.a. numerical differentiation (of discrete values)
    deltas = deltas + abs(utilizationPerQuarter[i] - utilizationPerQuarter[i - 1])
deltas = round(deltas, 5)


def getUtilization():
    actualUtilizationPerQuarter = []
    scale_factor = 0.85  # we do not model entries and exits that happen in the same time slice - this scale factor
    # accounts for that. Most likely it is even less we actually model in our utilization

    for day in range(len(driveInAndOut)):
        entry = driveInAndOut[''][day]  # todo set correct column label for entries
        exit = driveInAndOut[''][day]  # todo set correct column label for exits
        scaleFactor_deltas = (entry + exit) / deltas
        for quarter in range(len(utilizationPerQuarter)):
            actualUtilizationPerQuarter.\
                append(round(utilizationPerQuarter[quarter] * scaleFactor_deltas * scale_factor, 5))
    # shift utilization back to original coordinates
    actualUtilizationPerQuarter = actualUtilizationPerQuarter[-shift:] + actualUtilizationPerQuarter[:-shift]

    # plt.plot(actualUtilizationPerQuarter, color='black')
    # plt.title("Utilization")
    # plt.xlabel("Quarters")
    # # plt.show()
    # plt.savefig("plots/utilization_model.pdf")
    # plt.clf()

    return actualUtilizationPerQuarter


def getDateAndTime():
    dateAndTime = []
    quarters = [':00', ':15', ':30', ':45']

    for date in driveInAndOut['Datum']:
        for hour in range(0, 24):
            if hour < 10:
                hour = '0' + str(hour)
            else:
                hour = str(hour)
            for quarter in quarters:
                time = hour + quarter
                dateAndTime.append(date + ' ' + time)

    return dateAndTime


# actualUtilization = getUtilization()
# plt.bar(range(0, 96), actualUtilization[33888:33984], color='black')
# plt.title("Utilization")
# plt.xlabel("Quarters")
# plt.show()
#
# deltas = 0
# for i in range(33888, 33984):
#     # calculate finite differences a.k.a. numerical differentiation (of discrete values)
#     deltas = deltas + abs(actualUtilization[i] - actualUtilization[i - 1])
# deltas = round(deltas, 5)
# print(deltas, driveInAndOut[''][353], driveInAndOut[''][353])  # todo set column labels again, first entries, then exits
