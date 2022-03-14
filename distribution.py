#  import matplotlib.pyplot as plt
import numpy as np

__author__ = "Dr Nancy Retzlaff"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = ["Nancy Retzlaff"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Dr Nancy Retzlaff"
__email__ = "retzlaff@wifa.uni-leipzig.de"
__status__ = "Prototype"

# first mean (peak) is around 11:30 am ^= 11*4 + 2 = 46 (quarter hours)
# second mean (peak) around 5:00 pm ^= 12*4 + 5*4 = 68
# for further information see:
# https://www.neuss.de/leben/stadtplanung/verkehrsplanung/verkehrsuntersuchung-zur-erweiterung-des-gewerbegebietes-derikum/analyse/5-6-3.html

# we introduce a shift in our data to account for exits after midnight which would otherwise be cut off
# shift by 16 quarters of an hour = 4h
shift = 16
mean1 = 46 - shift
mean2 = 68 - shift
sd1 = 6
sd2 = 12


def normal_dist(x_, mean, sd):
    prob_density = 1 / (2 * np.pi * (sd ** 2)) * np.exp(-0.5 * ((x_ - mean) / sd) ** 2)
    return prob_density


def getCombinedDistribution():
    y = []
    for i in range(0, 96):
        y.append(round((normal_dist(i, mean1, sd1) +
                        5 * normal_dist(i, mean2, sd2)) * 100, 5))
    return y, shift

# fig, ax = plt.subplots(1, 1)
# x = np.linspace(0, 95, 96)
# dens1 = 100 * normal_dist(x, mean1, sd1, 96)  # easier to work with later
# dens2 = 500 * normal_dist(x, mean2, sd2, 96)
# utilization = getCombinedDistribution(96)
# utilization = utilization[shift:] + utilization[:shift]

# plt.plot(dens1)
# plt.plot(dens2, color='orange')
# plt.plot(utilization, color='black')
# plt.title("Einzelne Verteilungen der Auslastung mit 4h-Shift")
# plt.xlabel("Viertelstunden")
# plt.show()

# earlyBirds = []
# for i in range(0, 96):
#     earlyBirds.append(normal_dist(i, mean1, sd1, 96) * 100)
# earlyBirds = earlyBirds[-shift:] + earlyBirds[:-shift]

# sleepyHeads = []
# for i in range(0, 96):
#     sleepyHeads.append(5 * normal_dist(i, mean2, sd2, 96) * 100)
# sleepyHeads = sleepyHeads[-shift:] + sleepyHeads[:-shift]

# utilization = utilization[-shift:] + utilization[:-shift]
# plt.bar(range(0, 96), utilization, color='black', alpha=0.8)
# plt.bar(range(0, 96), earlyBirds, alpha=0.8)
# plt.bar(range(0, 96), sleepyHeads, color='orange', alpha=0.6)
# plt.title("Auslastung")
# plt.xlabel("Viertelstunden")
# #plt.show()
# plt.savefig('utilization.pdf')
