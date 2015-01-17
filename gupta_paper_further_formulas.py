from architecture_further_formulas import *

class gupta_paper:
	dictionary = dictionary()
	spiketimes = dictionary.spikeTimes(dictionaryLongitude, spikeInterval, spikesPerChar, epochs)
	testSpiketimes = spiketimes
	LIK = SpikeGeneratorGroup(N=15, indices=spiketimes[:,0], times=spiketimes[:,1]*ms)
	neuronIndex = 0
	t = 0.0000
	SummedDendriteGroup = 0;
	SynapseToSoma = 0;
	SigmaWDSyn = .0375 * mV
	SigmaWDSynMod = .5
	RmEq = Rm #Rm * mV
	DendR = .0375 * mV
	DendW = 1
	DendDirac = 1	
	# tauD and R lines below are to avoid an odd 'reference before assignment' error
	tauD = tauD
	testTauD = testTauD
	R = R
	testR = testR
	tauM = tauM
	lastSpikeInterval = 0.0
	currentEpoch = 0
	refractoryPointCounter = 0.0
	refractoryPointSwitch = False
	neuronIndexCounter = 0.0
	neuronIndexSwitch = False
	timing = []
	truePositiveSpikeResults = 0
	falsePositiveSpikeResults = 0
	trueNegativeSpikeResults = 0
	falseNegativeSpikeResults = 0
	totalSpikeIntervals = 12	
	testSpikesFiredInInterval = np.array([[False]*(totalSpikeIntervals+1)]*dictionaryLongitude)
	IdSpikeFired = np.array([[False]*numberOfPixels]*dictionaryLongitude); 
	testIdSpikeFired = np.array([[False]*numberOfPixels]*dictionaryLongitude); 
	IsSpikeFired = np.array([False]*dictionaryLongitude); 
	testIsSpikeFired = np.array([False]*dictionaryLongitude);	
	UmSpikeFired = np.array([False]*dictionaryLongitude); 
	testUmSpikeFired = np.array([False]*dictionaryLongitude); 
	IdRefractoryPeriod = np.array([[False]*numberOfPixels]*dictionaryLongitude); 
	testIdRefractoryPeriod = np.array([[False]*numberOfPixels]*dictionaryLongitude); 
	IsRefractoryPeriod = np.array([False]*dictionaryLongitude); 
	testIsRefractoryPeriod = np.array([False]*dictionaryLongitude); 
	UmRefractoryPeriod = np.array([False]*dictionaryLongitude); 
	testUmRefractoryPeriod = np.array([False]*dictionaryLongitude); 
	refractoryGraphingSwitch = False

	correctSpikes = np.array([[1]*totalSpikeIntervals]*dictionaryLongitude);#[[1] * totalSpikeIntervals]*dictionaryLongitude
	correctSpikes[0][3:12] = 0
	correctSpikes[1][0:3] = 0
	correctSpikes[1][6:12] = 0
	correctSpikes[2][0:6] = 0
	correctSpikes[2][9:12] = 0
	correctSpikes[3][0:9] = 0
    
	M = None
	testM = None
	UmM3 = None
	testUmM3 = None

	print 'initial Weights\n',W

	def run_model(self):
		
		dictionary = self.dictionary
		spiketimes = self.spiketimes
		eqs = Equations('''
			dv/dt = (-v+((RmZ/volt)*(IdVZ)))/(tauMZ) : volt (unless refractory)
			RmZ = 80*mV : volt
			tauMZ = 30*ms : second
			IdVZ : volt
	        V : volt
	        DendI : volt
	        SynI : volt
	        v2 : volt			
		    ''')			

		directToSomaEqs = Equations('''
			dv/dt = (-v+summedWandIDirac)/(tauMZ) : volt (unless refractory)
			tauMZ = 30*ms : second
			IdVZ : volt
	        V : volt
	        DendI : volt
	        SynI : volt
	        v2 : volt
			''')

		testEqs = Equations('''
			dvTest/dt = (-vTest+((RmTest/volt)*(IdVTest)))/(tauMTest) : volt (unless refractory)
			RmTest = 80*mV : volt
			tauMTest = 30*ms : second
			IdVTest : volt
	        VTest : volt
	        DendITest : volt
	        SynITest : volt
	        v2Test : volt
	        testUmSpikeFired : boolean		
		    ''')			



		myclock=Clock(dt=1*ms)
		testMyclock=Clock(dt=1*ms)

		ADDS = NeuronGroup(N=4, model=eqs,threshold='v>.01*mV', reset='v=-0.002 * mV; dv=0; IdVZ = 0*mV;v2=10*mV',refractory=10*ms,clock=myclock)
		testADDS = NeuronGroup(N=4, model=testEqs,threshold='vTest>.01*mV', reset='vTest=-0.002 * mV; dvTest=0; IdVZTest = 0*mV;v2Test=10*mV;testUmSpikeFired=True',refractory=10*ms,clock=testMyclock)

		def returnUm(self):
			# Main logic of the neuron simulation model is performed here
			# Modules are performed below resulting in voltage for the neurons being calculated

			dictionary = self.dictionary
			neuronIndex = self.neuronIndex
			t = self.t
			tNorm = t - (floor(t/spikeIntervalUnformatted) * spikeIntervalUnformatted) 
			spiketimes = self.spiketimes
			
			# Calculate tauD
			tauD = self.tauD
			tauD = tauDCalc(neuronIndex, tauD, W)
			#print 'main calc tauDCalc()', tauD

			# Calculate resistance
			R = self.R
			R = resistanceCalc(neuronIndex, tauD, R)
			#print 'main calc resistanceCalc()', R

			#Dedritic total post-synaptic current
			Id[neuronIndex], self.IdSpikeFired[neuronIndex], self.IdRefractoryPeriod[neuronIndex] = dentritePostSynapticCurrent(neuronIndex, Id, self.IdSpikeFired, self.IdRefractoryPeriod, R, W, spiketimes)
			#print 'neuronIndex',neuronIndex,'self.t',self.t,'ADDS.t',ADDS.t,'Id[neuronIndex]',Id[neuronIndex]
			# Direct to soma 

			### Soma membrane potential ###
			ADDS.IdVZ[neuronIndex] = totalSomaMembranePotential(neuronIndex, Id, Is, tNorm)

			# Refractory and spike evaluation: Is
			Is[neuronIndex], self.IsSpikeFired[neuronIndex], self.IsRefractoryPeriod[neuronIndex] = refractoryPeriodEvaluation(Is[neuronIndex], self.IsSpikeFired[neuronIndex], self.IsRefractoryPeriod[neuronIndex])
			Is[neuronIndex], self.IsSpikeFired[neuronIndex], self.IsRefractoryPeriod[neuronIndex] = spikeFiredEvaluation(Is[neuronIndex], self.IsSpikeFired[neuronIndex], self.IsRefractoryPeriod[neuronIndex])			

			timePeriodAndRefractoryCalcs()

			return Um[neuronIndex] * mV;	

		def refractoryPeriodEvaluation(Voltage, SpikeFired, RefractoryPeriod):
			# Check for spike
			# when identifying a spike, refractoryPeriodEndPoint is used as an alternative condition to refractoryPeriod being
			# over to allow a spike right at that end point

			# Refractory period
			#refractoryPeriodEndPoint = (self.t - 0.001) % spikeIntervalUnformatted <= 0.00001			
			if SpikeFired == True and self.refractoryPointSwitch == False:
				RefractoryPeriod = True
				#print 'refrac activated!'
			elif RefractoryPeriod == True and self.refractoryPointSwitch == True:
				# 0.001 added above for time step compatibility.   0.00001 instead of 0.0 used for some kind of 
				# modulo computational result offset in python which was producing a value from the modulo calc
				# just slightly over 0
				RefractoryPeriod = False
				#print 'refrac over!'
			#print 'self.refractoryPeriod == True and refractoryPeriodEndPoint', self.refractoryPeriod == True, refractoryPeriodEndPoint, (self.refractoryPeriod == True and refractoryPeriodEndPoint), self.t % (spikeIntervalUnformatted + 0.001) <= 0.00001
			if RefractoryPeriod == True:
				Voltage = Ureset			

			return [Voltage, SpikeFired, RefractoryPeriod]

		def spikeFiredEvaluation(Voltage, SpikeFired, RefractoryPeriod):			
			# Spike firing detection positioned here to allow Ureset value to occur on next timestep.
			# This allows spike to be recorded in plot instead of value immediately going to Ureset.
			SpikeFired = False
			if Voltage >= ActionPotentialThreshold and (RefractoryPeriod == False or refractoryPeriodEndPoint):
				#Um[neuronIndex] = Ureset
				#print 'Voltage',Voltage
				SpikeFired = True	

			return [Voltage, SpikeFired, RefractoryPeriod]

		def dentritePostSynapticCurrent(neuronIndex, IDend, IDendSpikes, IDendRefract, R, W, spiketimes):
			# Solving for Idend in the formula in the article yeilded the below equation
			t = self.t
			e = math.e
			#print ':::range(len(IDend[neuronIndex][:])\t','self.t\t',self.t,'\tneuronIndex\t',neuronIndex,'\t',IDend,'\t',IDend[neuronIndex]

			for IdIndex in range(len(IDend[neuronIndex][:])):
				tauDen = tauD[neuronIndex][IdIndex]
				r = R[neuronIndex][IdIndex]
				w = W[neuronIndex][IdIndex]

				# set tpresyn initially too far to trigger dirac
				#tPreSyn = -t - 1
				tPreSyn = t + 1
				for presynInd in range(shape(spiketimes)[0]):
					comparedSpikeTime = spiketimes[presynInd][1]
					#print 'comparedSpikeTime:::\t',comparedSpikeTime,'\t::self.lastSpikeInterval\t',self.lastSpikeInterval
					'''# spikeIntervalUnformatted included below to have offset where skiping input starting at .1 becomes 0.0, representing input spikes right from
					# 0.0 to 300 ms, as the input is intended
					# changed <= to < below to see if that works better
					if spiketimes[presynInd][0] == IdIndex and (comparedSpikeTime-spikeIntervalUnformatted) < t:'''
					# checking prior interval for a spike.  This looks for a spike in the prior spike time interval 
					#if spiketimes[presynInd][0] == IdIndex and comparedSpikeTime > (self.lastSpikeInterval - spikeIntervalUnformatted):
					#print 'self.t',self.t,'neuronIndex',neuronIndex,'spiketimes[presynInd][0]',spiketimes[presynInd][0],'comparedSpikeTime',comparedSpikeTime#,'self.lastSpikeInterval',self.lastSpikeInterval,'spikeIntervalUnformatted',spikeIntervalUnformatted,'IdIndex',IdIndex,'spiketimes[presynInd][0]',spiketimes[presynInd][0]
					if spiketimes[presynInd][0] == IdIndex and comparedSpikeTime >= (self.lastSpikeInterval - spikeIntervalUnformatted) and comparedSpikeTime <= self.lastSpikeInterval:
						tPreSyn = comparedSpikeTime

					# this is true? -> commented out logic below due to spiketimes perhaps not being in sorted order, a relevant entry could occur after an irrelevant one
					#if (comparedSpikeTime-spikeIntervalUnformatted) > t:
					# spike times are in order of earliest to latest times grouped with input pixel number.  therefore the below cutoff in the loop is fine.
					if comparedSpikeTime > self.lastSpikeInterval:
						break

				#print 'tPreSyn000:',tPreSyn
				Id2 = IDend[neuronIndex][IdIndex]
				Dt = t - tPreSyn
				# self.t == lines below are a workaround for initialization values
				if self.t == 0.121 or self.t == 0.421 or self.t == 0.721 or self.t == 1.021:
					Dt = 1.0
				# dirac function helps allow or disallow signal to be sent from input neurons through dendrite nodes or not
				# converted Dt to units which seem to make more sense for dirac function used, not sure if right to do that
				# though
				# simplify dirac for testing
				#DiracFun = 0
				DiracFun = 1/Dt

				#SpikeModCoeff = (r*w*DiracFun)

				# dirac test
				# t in dirac forumula means curent time or last spike time?		
				#if (t > -(Dt/2) and t < (Dt/2)):
				#if Dt <= spikeIntervalUnformatted:
				SpikeModCoeff = (r*w)
				
				#print '***ni:\t',neuronIndex,'\tIdIndex\t',IdIndex,'\t***w:\t',w

				# correct for scaling
				tauDen = tauDen * .001
				
				# normalize t to count just time within spike interval.  Formula from article just uses t in a way
				# relative to the spike interval it seems and therefore that approach is applied to the formula here.	
				tNorm = t - (floor(t/spikeIntervalUnformatted) * spikeIntervalUnformatted) 
				#if -Dt/2<(tNorm or t?)<Dt/2:
				#if Dt <= 0.0:
				if Dt >= 0.0:
					if self.t == 0.121 or self.t == 0.421 or self.t == 0.721 or self.t == 1.021:
						DiracFun = 1.00
					#SpikeModCoeff = .011
					#DiracFun = 0.66
					SpikeModCoeff = (SpikeModCoeff*DiracFun)
					#tauDen = .03	
					IDend[neuronIndex][IdIndex] = -(SpikeModCoeff - Id2) * (e ** (-tNorm/tauDen)) + SpikeModCoeff
					#print 'IDend2:\t',self.t,neuronIndex,IDend[neuronIndex]
				else:
					DiracFun = 0
					SpikeModCoeff = (SpikeModCoeff*DiracFun)															
					IDend[neuronIndex][IdIndex] = -(SpikeModCoeff - Id2) * (e ** (-tNorm/tauDen)) + SpikeModCoeff
					#print 'IDend2:\t',self.t,neuronIndex,IDend[neuronIndex]
				
				#print 'part1: \t',IDend
				#print 'factors\tSpikeModCoeff\t',SpikeModCoeff,'self.t',self.t,'neuronIndex',neuronIndex,'\tId2\t',Id2,'\ttPreSyn\t',tPreSyn,'\tDiracFun\t',DiracFun,'Dt <= 0.0',(Dt <= 0.0),'Dt',Dt,'\tneuronIndex\t',neuronIndex,'\tIdIndex\t',IdIndex,'-(SpikeModCoeff - Id2)',-(SpikeModCoeff - Id2),'-(SpikeModCoeff - Id2) * (e ** (-tNorm/tauDen))',-(SpikeModCoeff - Id2) * (e ** (-tNorm/tauDen))

				# Refractory and spike evaluation: Id
				#print 'part2: \t',refractResults
				#spikeEvalResults = spikeFiredEvaluation(refractResults[0], refractResults[1], refractResults[2])
				#print 'part3: \t',spikeEvalResults
				spikeEvalResults = IDend[neuronIndex][IdIndex], IDendSpikes[neuronIndex][IdIndex], IDendRefract[neuronIndex][IdIndex]
				if self.t > (self.lastSpikeInterval+0.02):
					refractResults = refractoryPeriodEvaluation(IDend[neuronIndex][IdIndex], IDendSpikes[neuronIndex][IdIndex], IDendRefract[neuronIndex][IdIndex])
					spikeEvalResults = spikeFiredEvaluation(refractResults[0], refractResults[1], refractResults[2])
				
				IDend[neuronIndex][IdIndex] = spikeEvalResults[0]
				#print 'IDend3:\t',self.t,neuronIndex,IDend[neuronIndex]
				IDendSpikes[neuronIndex][IdIndex] = spikeEvalResults[1]
				IDendRefract[neuronIndex][IdIndex] = spikeEvalResults[2]

				#print 'part1_2: \t', IDend
				
			return [IDend[neuronIndex], IDendSpikes[neuronIndex], IDendRefract[neuronIndex]]

		def somaPostSynapticCurrent(neuronIndex, ISoma, ISomaSpikes, ISomaRefract, R, W, spiketimes):
			'''### Synapse directly to soma ###
			# Solving for Id in the formula in the article yeilded the below equation
			# To calculate the DiracWeightedSum the spike times with the dirac function applied are multipled by the synapse weight 
			# and summed then divided by the number of synapses for the neuron 
			DiracWeightedSum = 0
			for DiracIndex in range(len(Is)):
				#tPreSyn = spiketimes[DiracIndex + (neuronIndex * len(Is))][0]
				tPreSyn = spiketimes[DiracIndex + (neuronIndex * len(Is)) + (self.currentEpoch*(dictionaryLongitude*numberOfPixels))][0]
				Dt = t - tPreSyn
				DiracFun = 1/Dt
				# dirac test  # TODO: not sure dirac is implemented correctly here
				if (t > -(Dt/2) and t < (Dt/2)):
					DiracFunctionWithSpikeTimes = DiracFun # (-t+tPreSyn)/tauDen
				else:
					DiracFunctionWithSpikeTimes = 0
				DiracWeightedSum = DiracWeightedSum + W[neuronIndex][WIndex] * DiracFunctionWithSpikeTimes
			DiracWeightedSum = DiracWeightedSum / len(Id)

			Is2 = Is[neuronIndex]

			#Is[neuronIndex] = -(DiracWeightedSum - Is2) * (e ** (-t/tauS)) + DiracWeightedSum
			Is[neuronIndex] = -(DiracWeightedSum - Is2) * (e ** (-tNorm/tauS)) + DiracWeightedSum'''

			return ['stub', 'stub', 'stub']

		def totalSomaMembranePotential(neuronIndex, IDend, ISoma, tNorm):
			### Soma membrane potential.  Now this method is just used for dendrite synapse output aggregation ###
			SummedDendriteGroup = sum(IDend[neuronIndex])*volt*10#*10 added 12/29/14 for scaling adjustment test # * 1 # the * 1000 is for a scaling adjustment
			# below removed until later needed
			#SynapseToSoma = ISoma[neuronIndex]
			#print 'self.epochIndex\t',self.epochIndex,'\tneuronIndex\t',neuronIndex,'\tSummedDendriteGroup\t',SummedDendriteGroup,'\tIDend\t',IDend
			return SummedDendriteGroup

		def WeightChangeCalculation():
			for inputNeuronIndex in range(numberOfPixels):
				## General STDP learning rule implementation ##
				# Find SpikePreSyn if it exists
				# Note: could replace this with use of dictionary data structure for lookups if convenient
				# for processing time later

				# SpikePreSyn not found than make it max distance from SpikePostSyn
				# TODO SpikePreSyn = 0.1 # (Max spike time interval distance)
				# round up to nearest 100ms interval
				SpikePreSyn = (math.ceil(self.t*10)*.1)*second
				# SpikePostSyn not found than make it max distance from SpikePreSyn
				# TODO SpikePostSyn = 0.0
				#SpikePostSyn = 0*ms
				SpikePostSyn = (math.floor(self.t*10)*.1)*second

				preSynSpikeFound = False
				postSynSpikeFound = False

				spikeCollection = spiketimes
				NumberOfSpikes = shape(spikeCollection)[0]
				for i in range(NumberOfSpikes):
					CurrentSpikeNueron = spikeCollection[i][0]
					CurrentSpikeTime = spikeCollection[i][1]*second

					# exit loop once values below current time elapsed have all been checked
					if CurrentSpikeTime > (self.t*second):
						#print 'eeww1:\tspiketimes\t',spiketimes,'\tqq\t',CurrentSpikeTime
						break

					# (self.t*second-.1*second) is to check if in relevant time window below.
					# Note: that may not be a good cut off and I should check it
					# added < self.t just for testing
					if CurrentSpikeNueron == inputNeuronIndex and CurrentSpikeTime > (self.t*second-.1*second):# and CurrentSpikeTime < (self.t*second):
						SpikePreSyn = CurrentSpikeTime
						preSynSpikeFound = True

				# Find SpikePostSyn if exists
				#spikeCollection = M.spikes
				spikeCollection = M.it
				#print 'spikeCollection',spikeCollection
				#print 'spikeCollection', spikeCollection
				NumberOfSpikes = len(spikeCollection[0])
				for i in range(NumberOfSpikes):
					#CurrentSpikeNueron = spikeCollection[i][0]
					#CurrentSpikeTime = spikeCollection[i][1]*1000
					CurrentSpikeNueron = spikeCollection[0][i]
					#CurrentSpikeTime = spikeCollection[1][i]*1000
					CurrentSpikeTime = spikeCollection[1][i]*10
					#print 'CurrentSpikeNueron',CurrentSpikeNueron,'CurrentSpikeTime',CurrentSpikeTime,'self.t*second',self.t*second

					# exit loop once values below current time elapsed have all been checked
					# Disabled due to spikeCollection not being sorted and causing break too early
					#if CurrentSpikeTime > (self.t*second):
					#	break

					# (self.t*second-.1*second) is to check if in relevant time window below.
					# Note: that may not be a good cut off and I should check it
					# * Important difference: CurrentSpikeNueron is compared to self.neuronIndex and not inputNeuronIndex here
					# added (.1+.008)
					if CurrentSpikeNueron == self.neuronIndex and CurrentSpikeTime >= (self.t*second-(.1+.008)*second) and CurrentSpikeTime <= (self.t*second):
						SpikePostSyn = CurrentSpikeTime	
						postSynSpikeFound = True	

				if preSynSpikeFound == False or postSynSpikeFound == False:
					# Todo: watch more for spikes in a relevant time frame but are actually from different synapses and would
					# give different results?  could cause unwanted results? brain would know synapse difference?

					## todo: currently included is logic for processing if SpikePostSyn or SpikePreSyn were not found?

					if preSynSpikeFound == False and postSynSpikeFound == True:
						SpikePreSyn = SpikePostSyn + .1*second
						#print 'F T'
					elif preSynSpikeFound == True and postSynSpikeFound == False:
						# Note: does postSynSpikeFound need to be true for the weight to be allowed to increase?
						SpikePostSyn = SpikePreSyn - .1*second
						#print 'T F'
					#else:
						#print 'F F'

				#SpikePreSyn = 500*ms
				#SpikePostSyn = 700*ms
				#print 'neuronIndex', self.neuronIndex, 'inputNeuronIndex',inputNeuronIndex,'self.t', self.t, 'ADDS.v2',ADDS.v2, 'preSynSpikeFound',preSynSpikeFound,'postSynSpikeFound',postSynSpikeFound,'SpikePostSyn', SpikePostSyn, 'SpikePreSyn', SpikePreSyn

				# Find DeltaW
				DeltaW = returnDeltaW(SpikePreSyn, SpikePostSyn)  

				# Find new weight
				WOld = W[self.neuronIndex][inputNeuronIndex];

				W[self.neuronIndex][inputNeuronIndex] = returnNewW(WOld, DeltaW);

		def returnDeltaW(SpikePreSyn, SpikePostSyn):
			DeltaSpikeTime = SpikePreSyn - SpikePostSyn
			# TODO: figure out if DeltaW = 0 is really fine for init value
			DeltaW = 0
			# changed below line from that content in the article for a workaround/temp fix
			#if DeltaSpikeTime < 0:
			if DeltaSpikeTime <= 0:
				DeltaW = APlus * (e ** (DeltaSpikeTime / (TauPlus*ms)))
				# for testing
				DeltaW = 1
			elif DeltaSpikeTime > 0:
				DeltaW = AMinus * (e ** (-DeltaSpikeTime / (TauMinus*ms)))	
				# for testing
				DeltaW = -1

			# testing
			#print 'self.t',self.t,'SpikePreSyn',SpikePreSyn,'SpikePostSyn',SpikePostSyn,'DeltaSpikeTime',DeltaSpikeTime,'DeltaW',DeltaW
			#if 	(t*ms) - SpikePreSyn > (1*ms):
			#	DeltaW = .5
			#else:
			#	DeltaW = -.5				

			return DeltaW

		def returnNewW(WOld, DeltaW):
			# W is weight
			synapseType = 'excitatory'
			# Default 'excitatory' values
			WMin = 0;
			WMax = 1;
			if synapseType == 'inhibitory':
				WMin = -1;
				WMax = 0;		
				
			#print 'DeltaW', DeltaW
			## Relaxation rule implementation ##
			if DeltaW >= 0:				
				WNew = WOld + (LearningRate * (DeltaW * (WMax - WOld)))
				
			elif DeltaW < 0:	
				WNew = WOld + (LearningRate * (DeltaW * (WOld - WMin)))
			#print 'WOld', WOld
			#print 'WNew', WNew

			return WNew;
			##			

		def evaluateClassifier():
			tNorm = self.t - (floor(self.t/spikeIntervalUnformatted) * spikeIntervalUnformatted) 

			testR = [[1] * numberOfPixels]*dictionaryLongitude
			'''testW = [[1, 0, 1,0, 1, 0,0, 0, 0,0, 1, 0,0, 1, 0],
			[0, 0, 1,0, 1, 0,0, 0, 1,0, 1, 0,0, 0, 1],
			[0, 0, 0,0, 1, 1,0, 1, 1,0, 1, 1,0, 0, 0],
			[0, 0, 1,0, 1, 0,0, 1, 0,0, 1, 0,0, 0, 1]]'''
			testW = [[ 0.69607004, 0.00413144, 0.91697601, 0.00360609, 0.91761815, 0.00445725, 0.00340361, 0.22605207, 0.0039314, 0.00451545, 0.91885474, 0.00333926, 0.00245632, 0.69608306, 0.22541202],
			[ 0.29794995, 0.0025975, 0.99158123, 0.00318387, 0.99296564, 0.00275211, 0.00305578, 0.0027208, 0.69734084, 0.00306026, 0.99202054, 0.00387052, 0.00440005, 0.29888318, 0.69716381],
			[ 0.0048261, 0.00419521, 0.33389914, 0.00392254, 0.96962399, 0.64231264, 0.00371715, 0.64278451, 0.97156676, 0.00332437, 0.96967301, 0.64113085, 0.00312674, 0.00290903, 0.33244029],
			[ 0.00562191, 0.00532413, 0.66298468, 0.00350251, 0.9567765, 0.29948389, 0.00621025, 0.9585158, 0.30201652, 0.00402158, 0.95678115, 0.30231021, 0.00520207, 0.00577489, 0.66244477]]

			# for each charactor input below test the classfication results
			for neuronIndex in range(dictionaryLongitude):
				# Calculate tauD
				testTauD = self.testTauD
				testTauD = tauDCalc(neuronIndex, testTauD, testW)
				#print 't:',self.t,'neuronIndex',neuronIndex,'main calc tauDCalc()', testTauD

				# Calculate resistance
				testR = self.testR
				testR = resistanceCalc(neuronIndex, testTauD, testR)

				#Sample output for testing
				testR = [[0.01016803758319553, 0.010171374818041036, 0.0083665317732988555, 0.01017281704840039, 0.0048279096384584727, 0.0071335782968518762, 0.010173903373815114, 0.0071306637775638056, 0.0048108924488047102, 0.010175980702300289, 0.0048274813185357644, 0.0071408747375879501, 0.010177025843651875, 0.010178177167130422, 0.0083748475057425463],
				[0.01016803758319553, 0.010171374818041036, 0.0083665317732988555, 0.01017281704840039, 0.0048279096384584727, 0.0071335782968518762, 0.010173903373815114, 0.0071306637775638056, 0.0048108924488047102, 0.010175980702300289, 0.0048274813185357644, 0.0071408747375879501, 0.010177025843651875, 0.010178177167130422, 0.0083748475057425463],
				[0.01016803758319553, 0.010171374818041036, 0.0083665317732988555, 0.01017281704840039, 0.0048279096384584727, 0.0071335782968518762, 0.010173903373815114, 0.0071306637775638056, 0.0048108924488047102, 0.010175980702300289, 0.0048274813185357644, 0.0071408747375879501, 0.010177025843651875, 0.010178177167130422, 0.0083748475057425463],
				[0.01016803758319553, 0.010171374818041036, 0.0083665317732988555, 0.01017281704840039, 0.0048279096384584727, 0.0071335782968518762, 0.010173903373815114, 0.0071306637775638056, 0.0048108924488047102, 0.010175980702300289, 0.0048274813185357644, 0.0071408747375879501, 0.010177025843651875, 0.010178177167130422, 0.0083748475057425463]]

				#print 't:',self.t,'neuronIndex',neuronIndex,'main calc resistanceCalc()', testR

				testId[neuronIndex], self.testIdSpikeFired[neuronIndex], self.testIdRefractoryPeriod[neuronIndex] = dentritePostSynapticCurrent(neuronIndex, testId, self.testIdSpikeFired, self.testIdRefractoryPeriod, testR, testW, self.testSpiketimes)
				#print 'neuronIndex2',neuronIndex,'self.t',self.t,'testADDS.t',testADDS.t,'testId[neuronIndex]',testId[neuronIndex],'testADDS.v2Test',testADDS.v2Test
				testIs = None
				testADDS.IdVTest[neuronIndex] = totalSomaMembranePotential(neuronIndex, testId, testIs, tNorm)
				
		def tauDCalc(neuronIndex, tau, W):
			# Weight loop
			for WIndex in range(len(W[0][:])):
				if abs(W[neuronIndex][WIndex]) <= 1:
					tau[neuronIndex][WIndex] = tauMax - abs(W[neuronIndex][WIndex])*(tauMax-tauMin)

			return tau

		def resistanceCalc(neuronIndex, tau, R):
			tauM = self.tauM
			#Resistance loop
			for RIndex in range(len(R[0][:])):				
				if (tau[neuronIndex][RIndex]*.001 == tauM):
					# avoid a division by 0 issue
					tauM = tauM - .000001

				R[neuronIndex][RIndex] = (((tau[neuronIndex][RIndex]*.001)*neuronFiringThreshold) / Rm) * ((tauM / (tau[neuronIndex][RIndex]*.001) ) ** (tauM / (tauM - (tau[neuronIndex][RIndex]*.001) )))

			return R

		def timePeriodAndRefractoryCalcs():
			neuronIndex = self.neuronIndex
			refractoryPointCounter = self.refractoryPointCounter
			refractoryPointSwitch = self.refractoryPointSwitch
			neuronIndexCounter = self.neuronIndexCounter
			neuronIndexSwitch = self.neuronIndexSwitch
			t = self.t
			
			# changed time step time for testing
			#timeStepInterval = 0.01
			#timeStepInterval = 0.002
			timeStepInterval = 0.001
			t = t + timeStepInterval
			self.timing.append(t)
			refractoryPointCounter = refractoryPointCounter + timeStepInterval
			neuronIndexCounter = neuronIndexCounter + timeStepInterval

			# At the end of each spike time interval refractory period is turned off and weight changes
			# are calculated.  Refractory turning off here * is not correct * because it can occur for
			# less than the set refractory period.  I am just using it for the time being for testing.
			refractoryPointSwitch = False
			if refractoryPointCounter >= spikeIntervalUnformatted:
				#refractoryPointCounter = 0.009
				refractoryPointCounter = 0.000
				refractoryPointSwitch = True
				self.lastSpikeInterval = self.t
				WeightChangeCalculation()
				# Report weights at different times
				#if self.t == 1.081 or self.t == 2.081 or self.t == 4.081 or self.t == 8.081 or self.t == 12.081:
				'''if self.currentEpoch == 2 or self.currentEpoch == 4 or self.currentEpoch == 8 or self.currentEpoch == 10 or self.currentEpoch == 12:
					print 'self.t:\t',self.t,'\tself.currentEpoch\t',self.currentEpoch,'\tcurrent neuront\t',self.neuronIndex
					print '0',W[0][:]
					print '1',W[1][:]
					print '2',W[2][:]
					print '3',W[3][:]'''

			neuronIndexSwitch = False
			if neuronIndexCounter >= (spikeIntervalUnformatted*3):
				#neuronIndexCounter = 0.009
				neuronIndexCounter = 0.0000
				neuronIndexSwitch = True
				# add epoch every epoch ms duration.  Occurs when a full series of input charactors has
				# occured and a new one starts.  self.neuronIndex == 3 really means it will roll back to
				# self.neuronIndex == 3 after neuronIndex is added
				if self.neuronIndex == 3:
					self.currentEpoch = self.currentEpoch + 1				

			# revision of when new neuron index is used.  new neuron every 300ms
			if neuronIndexSwitch == True:
				neuronIndex = neuronIndex + 1

			if neuronIndex == 4: 
				neuronIndex = 0

			self.neuronIndex = neuronIndex
			self.t = t
			self.refractoryPointCounter = refractoryPointCounter
			self.refractoryPointSwitch = refractoryPointSwitch
			self.neuronIndexCounter = neuronIndexCounter			
			self.neuronIndexSwitch = neuronIndexSwitch

		def OutputEvaluationResults(W, R, dictionaryLongitude):
			print 'Final Weights\n0',W[0][:]
			print '1',W[1][:]
			print '2',W[2][:]
			print '3',W[3][:]
			print 'Final Res\n0',R[0][:]
			print '1',R[1][:]
			print '2',R[2][:]
			print '3',R[3][:]		
			print '\n'
			print '+++ Results +++'
			print 'Spike results: TP:\t',self.truePositiveSpikeResults,'\tFP:\t',self.falsePositiveSpikeResults,'\tTN:\t',self.trueNegativeSpikeResults,'\tFN:\t',self.falseNegativeSpikeResults
			print 'totalSpikeIntervalsTested:\t',self.totalSpikeIntervals,'\ttotalCharsPresented:\t',dictionaryLongitude
			print 'True positives correct percentage (TP/totalSpikeIntervalsTested):\t',Decimal(format(self.truePositiveSpikeResults, '.1f'))/Decimal(format(self.totalSpikeIntervals, '.1f')),'\t(this is the percentage of all true positves that were found)'
			print 'Total correct percentage (TP+TN/(totalSpikeIntervals*totalCharsPresented)):\t',(Decimal(format(self.truePositiveSpikeResults, '.1f'))+Decimal(format(self.trueNegativeSpikeResults, '.1f')))/(Decimal(format(self.totalSpikeIntervals, '.1f'))*Decimal(format(dictionaryLongitude, '.1f')))
			print '+++++++++++++++'

		# This network_operation runs the membrane potential calculation function for every milisecond that occurs.
		# The Um output is saved directly to the ADDS V (voltage) records for use with Brian's code.
		@network_operation
		def myoperation():
			#print 'neuronIndex', self.neuronIndex, 'self.t', self.t, 'refractoryPointCounter',self.refractoryPointCounter,'ADDS.t', ADDS.t, 'ADDS.v[0]', ADDS.v
			#print 'neuronIndex', self.neuronIndex, 'self.t', self.t, 'ADDS.t', ADDS.t, 'ADDS.IdVZ[0]', ADDS.IdVZ
			returnUm(self)
			spikeIntervalCounter = (floor(self.t/spikeIntervalUnformatted) * spikeIntervalUnformatted)*10

			for vCheck in range(len(ADDS.v2)):
				if ADDS.v2[vCheck] == 10*mV:
					ADDS.v2[vCheck] = 0*mV

			for vCheck in range(len(testADDS.v2Test)):
				if testADDS.v2Test[vCheck] == 10*mV:
					testADDS.v2Test[vCheck] = 0*mV					

			# classifier performance test
			evaluateClassifier()

			# Only evaluate results for enough epochs to test each char in input (3 spike interv per char * 4 char = 12 spike intervals total)
			# the +1 in (self.totalSpikeIntervals+1) is to allow a last refractoryPointSwitch triggered negative spike evaluation to occur.
			if spikeIntervalCounter < (self.totalSpikeIntervals+1):
				for neuronIndex in range(dictionaryLongitude):				
					# Negative results below are only set to be measured after a full spike interval has passed and had the opportunity to have created a spike
					# (spikeIntervalCounter-1) is to correct for refractoryPointSwitch occuring after spikeInterval it addresses.
					if self.refractoryPointSwitch == true and (spikeIntervalCounter > 0):
						if self.testSpikesFiredInInterval[neuronIndex][spikeIntervalCounter-1] == False:
							if (self.correctSpikes[neuronIndex][(spikeIntervalCounter-1)] == 1):
								self.falseNegativeSpikeResults = self.falseNegativeSpikeResults + 1		
							else:
								self.trueNegativeSpikeResults = self.trueNegativeSpikeResults + 1	

						if (testADDS.testUmSpikeFired[neuronIndex] == True) and (spikeIntervalCounter < self.totalSpikeIntervals):
							if (self.correctSpikes[neuronIndex][spikeIntervalCounter] == 1):
								self.truePositiveSpikeResults = self.truePositiveSpikeResults + 1	
							else:
								self.falsePositiveSpikeResults = self.falsePositiveSpikeResults + 1	
							self.testSpikesFiredInInterval[neuronIndex][spikeIntervalCounter] = True	
							testADDS.testUmSpikeFired[neuronIndex] = False

						#self.testSpikesFiredInInterval[neuronIndex][spikeIntervalCounter] = False
						print 'self.t',self.t,'neuronIndex',neuronIndex,'Spike results: TP:\t',self.truePositiveSpikeResults,'\tFP:\t',self.falsePositiveSpikeResults,'\tTN:\t',self.trueNegativeSpikeResults,'\tFN:\t',self.falseNegativeSpikeResults

		M = SpikeMonitor(ADDS)
		self.M = M # for ipython compatibility
		testM = SpikeMonitor(testADDS)
		self.testM = testM
		Mv = StateMonitor(ADDS, 'V', record=True)
		MDendI = StateMonitor(ADDS, 'DendI', record=True)
		MSynI = StateMonitor(ADDS, 'SynI', record=True)
		UmM3 = StateMonitor(ADDS, 'v2', record=True)
		self.UmM3 = UmM3 # for ipython compatibility
		testUmM3 = StateMonitor(testADDS, 'v2Test', record=True)
		self.testUmM3 = testUmM3

		#totalRunTime = 21
		#run(totalRunTime*ms,threads=2, report='text')
		run(119*ms,report='text') # Run with enough time for scoring evaluation
		#run(2000*ms,report='text')

		# Present results and logging
		if presentResults == True:
			for epochIndex in epochsToPrint:
				reportResultsAndLogging = report_results_and_logging(dictionaryLongitude, epochsToPrint, M, Mv, epochIndex, spikeIntervalUnformatted, dictionary, epochMsDuration)
				reportResultsAndLogging.presenter()	

		# Show all membrane potentials
		# if statement with epochIndex below is to filter only epochs actaully included in a run
		if displayAllNeuronMemPotentials == True:
			for neuronIdentity in range(dictionaryLongitude):
				for epochIndex in epochsToPrint:
					if epochIndex <= totalRunTime/100:
						for epochMs in range(epochMsDuration):
							print 'neuron\t', neuronIdentity, '\tepochIndex\t', epochIndex, '\tepochMs\t', epochMs, '\tMembranePotential\t', Mv[neuronIdentity][(epochIndex*epochMsDuration)+epochMs]

		if logger == True:
			outputFile = open('snnResults.txt', 'w')	
			for epochIndex in range(epochs):
				reportResultsAndLogging = report_results_and_logging(dictionaryLongitude, epochsToPrint, M, Mv, epochIndex, spikeIntervalUnformatted, dictionary, epochMsDuration)
				reportResultsAndLogging.logger(outputFile)
			outputFile.close()

		OutputEvaluationResults(W, R, dictionaryLongitude)

		neuronToPlot = 1
		subplot(211)
		plot(M.t/ms, M.i, '.')
		subplot(221)
		plot(testM.t/ms, testM.i, '.')
		subplot(223)
		#plot(UmM3.t, UmM3.v2.T/mV)
		plot(UmM3.t, UmM3.v2.T/mV)
		xlabel('Time (ms)')
		ylabel('Membrane Potential (mV)')
		subplot(224)
		#plot(UmM3.t, UmM3.v2.T/mV)
		plot(testUmM3.t, testUmM3.v2Test.T/mV)
		xlabel('Time (ms)')
		ylabel('Membrane Potential (mV)')
		show()

	def __init__(self):
		self.run_model()

def main():
	run_gupta_paper = gupta_paper()

if  __name__ =='__main__':main()
