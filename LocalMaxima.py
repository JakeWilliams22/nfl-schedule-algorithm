import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from peakutils.peak import indexes

# dataSet = np.random.random(100)
# localMaxIndices = argrelextrema(dataSet, np.greater)
# localMax = [dataSet[localMaxIndices] for i in localMaxIndices]
# plt.plot(dataSet)
# plt.plot(localMaxIndices, localMax, 'rs')
# plt.show()


vector = [ 0, 6, 25, 20, 15, 8, 15, 6, 0, 6, 0, -5, -15, -3, 4, 10, 8, 13, 8, 10, 3, 1, 20, 7, 3, 0 ]
print('Detect peaks with minimum height and distance filters.')
indexes = indexes(np.array(vector), thres=2.0/max(vector), min_dist=2)
print('Peaks indexes are: %s' % (indexes))
# print ('Peaks are: %s' % (vector[indexes]))
peaks = []
for x in range(0, len(indexes)):
    temp = indexes[x]
    peaks.append(vector[temp])
plt.plot(vector)
# plt.plot(vector[indexes], 'ro')
plt.plot(indexes, peaks, 'ro')
plt.show()


# dataSet = np.random.random(100)
# localMaxIndices = argrelextrema(dataSet[0:(len(dataSet)/4)], np.greater)
# localMax = [dataSet[localMaxIndices] for i in localMaxIndices]
# plt.plot(dataSet)
# plt.plot(localMaxIndices[, np.amax(localMax), 'rs')
# plt.show()