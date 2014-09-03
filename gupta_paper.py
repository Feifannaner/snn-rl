from dictionary import *
from report_results_and_logging import *
import numpy as np
from brian import *

epochs = 100 
spikeMiliseconds = 100
spikeInterval = spikeMiliseconds * ms
spikeIntervalUnformatted = spikeMiliseconds * .001
dictionaryLongitude = 4
spikesPerChar=3
totalTime = epochs * spikesPerChar * dictionaryLongitude * spikeInterval 
epochsToPrint = [0,1,2,25,50,75]
presentResults = True
logger = True

dictionary = dictionary()
spiketimes = dictionary.spikeTimes(dictionaryLongitude, spikeInterval, spikesPerChar, epochs)
print ('spikeTimes2:')
print (spiketimes)
print (spiketimes.shape)
LIK = SpikeGeneratorGroup(15, spiketimes)


taum = 20 * ms
taue = 1 * ms
taui = 10 * ms
Vt = 5 * mV
Vr = 0 * mV

eqs = Equations('''
	  dV/dt  = (-V+ge-gi)/taum : volt
	  dge/dt = -ge/taue        : volt
	  dgi/dt = -gi/taui        : volt
	  ''')
ADDS = NeuronGroup(N=4, model=eqs,threshold=Vt, reset=Vr)


exhitatory = Connection(LIK, ADDS , 'ge',delay=10*ms,structure='dense')
Wexhitatory = np.random.uniform(10,50,[15,4]) * mV
exhitatory.connect(LIK,ADDS,Wexhitatory)
Ap = 1 * mV
Am = 1 * mV
stdp=ExponentialSTDP(exhitatory,taue,taum,Ap,Am,wmax=50 * mV,interactions='all',update='additive')


inhibitory = Connection(ADDS, ADDS , 'gi',delay=5*ms,structure='dense')
#Connect adds layer via lateral inhibitory connections
#the diagonal should be 0 to not auto-inhibate
Winhibitory = np.random.uniform(0,5,[4,4]) * mV
diagonal = np.diag_indices(Winhibitory.shape[0])
Winhibitory[diagonal] = 0;

inhibitory.connect(ADDS,ADDS,Winhibitory)

M = SpikeMonitor(ADDS)
Mv = StateMonitor(ADDS, 'V', record=True)
Mge = StateMonitor(ADDS, 'ge', record=True)
Mgi = StateMonitor(ADDS, 'gi', record=True)

run(10000*ms,threads=2, report='text')

# Present results and logging
if presentResults == True:
	for epochIndex in epochsToPrint:
		reportResultsAndLogging = report_results_and_logging(dictionaryLongitude, epochsToPrint, M, Mv, epochIndex, spikeIntervalUnformatted, dictionary)
		reportResultsAndLogging.presenter()	

if logger == True:
	outputFile = open('snnResults.txt', 'w')	
	for epochIndex in range(epochs):
		reportResultsAndLogging = report_results_and_logging(dictionaryLongitude, epochsToPrint, M, Mv, epochIndex, spikeIntervalUnformatted, dictionary)
		reportResultsAndLogging.logger(outputFile)
	outputFile.close()

neuronToPlot = 1
subplot(211)
raster_plot(M, title='The gupta network', newfigure=False)
subplot(223)
plot(Mv.times / ms, Mv[neuronToPlot] / mV)
xlabel('Time (ms)')
ylabel('V (mV)')
subplot(224)
plot(Mge.times / ms, Mge[neuronToPlot] / mV)
plot(Mgi.times / ms, Mgi[neuronToPlot] / mV)
xlabel('Time (ms)')
ylabel('ge and gi (mV)')
legend(('ge', 'gi'), 'upper right')
show()
