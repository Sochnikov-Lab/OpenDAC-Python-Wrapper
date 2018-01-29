import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import numpy as np #for future DFT


datafile = pd.read_csv("data.csv",sep=",")
times = datafile["time(s)"]
ch0V = datafile["ch0(V)"] #50Ohm
ch1V = datafile["ch1(V)"] #Open

pltfig = plt.figure()
ax = plt.gca()
#ax.scatter(times,ch0V, c='r', label="50 $\Omega$ Termination")
ax.scatter(times,ch0V, c='b', label="Sine Wave")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage")
print len(times)
ax.legend()

plt.show()
pltfig.savefig('figdata_tt.png')
