#!/usr/bin/env python
# Requires PyHLA, see http://www.nongnu.org/certi/PyHLA
import hla.rti
import hla.omt as fom

import struct

def log (valor):
	print ("\033[34m" + valor + "\033[0;0m")

class MyAmbassador(hla.rti.FederateAmbassador):
	def initialize(self):
		self.advanceTime = False
		self.time = None
		self.isConstrained = False
		self.isRegulated = False
		self.isRegistered = False
		self.isAnnounced= False
		self.isReady = False
		#######  Ajustando objetos ###########
                self.classHandle = rtia.getObjectClassHandle("ObjectRoot.robot")

                self.batteryHandle = rtia.getAttributeHandle("battery", self.classHandle)
                self.temperatureHandle = rtia.getAttributeHandle("temperature", self.classHandle)
                self.sensor1Handle = rtia.getAttributeHandle("sensor1", self.classHandle)
                self.sensor2Handle = rtia.getAttributeHandle("sensor2", self.classHandle)
                self.sensor3Handle = rtia.getAttributeHandle("sensor3", self.classHandle)
                self.gpsHandle = rtia.getAttributeHandle("gps", self.classHandle)
                self.compassHandle = rtia.getAttributeHandle("compass", self.classHandle)
                self.gotoHandle = rtia.getAttributeHandle("goto", self.classHandle)
                self.rotateHandle = rtia.getAttributeHandle("rotate", self.classHandle)
                self.activateHandle = rtia.getAttributeHandle("activate", self.classHandle)
		##################################### ADICIONADO EM TESTES #####################
		rtia.subscribeObjectClassAttributes(self.classHandle,[self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
		#####################################
                rtia.publishObjectClass(self.classHandle,[self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
                self.myObject = rtia.registerObjectInstance(self.classHandle)#, "ROBO_1")
		#####################################

	def terminate(self):
		rtia.deleteObjectInstance(self.myObject, "ROBO_1")

	# RTI callbacks
	def startRegistrationForObjectClass(*params):
		print("START", params)

	def provideAttributeValueUpdate(*params):
		print("PROVIDE UAV", params)

	def synchronizationPointRegistrationSucceeded(self, label):
		self.isRegistered = True
		self.log("MyAmbassador: Synchronization Point Registration Succeded\n")

	def announceSynchronizationPoint(self, label, tag):
		self.isAnnounced = True
		self.log("MyAmbassador: Announce Synchronization Point\n")


	def federationSynchronized (self, label):
		self.isReady = True
		self.log("MyAmbassador: Federation Synchronized\n")

	def timeRegulationEnabled (self, time):
		self.isRegulated = True
		self.log("MyAmbassador: Time Regulation Enabled\n")

	def timeConstrainedEnabled (self, time):
		self.isConstrained = True
		self.log("MyAmbassador: Time Constrained Enabled\n")
	def timeAdvanceGrant (self, time):
		self.advanceTime = True

	def log(self, valor):
		print ("\033[36m" + valor + "\033[0;0m")

### APENAS TESTANDO POSSIBILIDADE DE RECEBER DADOS #############
	def reflectAttributeValues(self, object, attributes, tag, order, transport, time=None, retraction=None):
		bateria = None
		temperatura = None
		gps = None
		if self.gpsHandle in attributes:
			gps = attributes[self.gpsHandle]
		if self.batteryHandle in attributes:
			bateria = attributes [self.batteryHandle]
			#print("REFLECT", attributes[self.batteryHandle])
			#print("Alguma coisa nao esta certa aqui")
			#pass

		if self.temperatureHandle in attributes:
			#print("REFLECT", attributes[self.temperatureHandle])
			valor = attributes[self.temperatureHandle]
			temperatura = valor
			"""valor =  valor.split(":")[1]
			valor =  valor.replace("\"", "")
			valor =  valor.replace("\\", "")
			valor =  valor.replace(">", "")
			valor =  valor.replace("<", "")
			x, y  = valor.split(";")
			import time
			time.sleep(1)
			print ("valor x : " + str (x) + " valor y : " + str (y))"""
			#print ("Received value: ", valor)
			if (int (x) != 0):
				#TODO Do something
				#self.ser.write("<"+ str(x)+ ":" + str( y )+ ">")
				#print ("dados enviados ao Arduino")
				pass


		if self.sensor1Handle in attributes:
			#print("REFLECT", attributes[self.sensor1Handle])
			pass#print("REFLECT", attributes[self.sensor1Handle])
		self.log("Valores recebidos : Bateria: " +str (bateria) + "; Temperatura: " + str(temperatura) + "; GPS: " + str (gps))

	def discoverObjectInstance(self, object, objectclass, name):
		print("DISCOVER", name)
		rtia.requestObjectAttributeValueUpdate(object,[self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])


	def startRegistrationForObjectClass(*params):
		print("START", params)

	def provideAttributeValueUpdate(*params):
		print("PROVIDE UAV", params)






print "\n --------x  Starting Python Aplication   x---------"
print ("Create ambassador")
rtia = hla.rti.RTIAmbassador()


####### Try Create a Federation ##############
try:
    rtia.createFederationExecution("ExampleFederation", "PyhlaToPtolemy.fed")
    log("Federation created.\n")
except hla.rti.FederationExecutionAlreadyExists:
    log("Federation already exists.\n")




####### Join into a Federation ###############
mya = MyAmbassador()
rtia.joinFederationExecution("uav-send", "ExampleFederation", mya)

mya.initialize()


log("inicialized!\n")

""" este codigo vai apenas no SlaveFederate
label = "ReadyToRun"
tag =  bytes ("hi!")
rtia.registerFederationSynchronizationPoint(label, tag)
print("Synchronization Point Registered!")
"""
######## Wait for users   ######################

x = input ("WAITING FOR USERS!\n")


######### Announce Synchronization Time #########

while (mya.isAnnounced == False):
	rtia.tick()
rtia.synchronizationPointAchieved("ReadyToRun")

while (mya.isReady == False):
	rtia.tick()


########## Time Organization ###################
federateTime = rtia.queryFederateTime()
lookahead = rtia.queryLookahead()
rtia.enableTimeRegulation(federateTime, lookahead)

while (mya.isRegulated == False ):
	rtia.tick()

rtia.enableTimeConstrained()

while (mya.isConstrained == False):
	rtia.tick()
###############################################




try:
	a= 1.0
	import random
	temperatura = 25
	contBateria = 1
	bateria= 100
	x = 0
	y = 0
	z = 0
	########## Main Loop ###########
	while(1):
                if (bateria> 5):
                        x = random.sample([x+ -2, x+ -1,x, x+ 1, x + 2, x, x], 1)[0]
                        y = random.sample([x+ -2, x+ -1,x, x+ 1, x + 2, y, y], 1)[0]
                        z = random.sample([x+ -2, x+ -1,x, x+ 1, x + 2, z, z], 1)[0]
                        temperatura+= random.sample([-1, -2, 0 ,1,2 ,3, 1, 2, 0, 0], 1)[0]
                else:
                        temperatura+= random.sample([-1, -2, -3, 0 ,1,2,-1,-2], 1)[0]
                contBateria+=1
                if (contBateria%3 == 0 and bateria> 5):
                        bateria-= 1
                #### publish and subscribe #####
                print ("ENVIADOS : Temperatura: "+ str(temperatura) + " bateria : " + str ( bateria ))
                a = a + 1.0
                rtia.updateAttributeValues(mya.myObject,
                        {mya.batteryHandle:str(bateria)+str(" "),
                        mya.temperatureHandle: str(temperatura)+" ",
                        mya.sensor1Handle:"sensor1",
                        mya.sensor2Handle:"sensor2",
                        mya.sensor3Handle:"sensor3",
                        mya.gpsHandle: str(str(x)+ ", " + str(y) + ", "+ str(z) + " "),
                        mya.compassHandle:"compasso",
                        mya.gotoHandle:"noGoto",
                        mya.rotateHandle:"noRotate",
                        mya.activateHandle:"noActivate"},
                        "update")
		#rtia.tick(1.0, 1.0)

		###### Time management ##########
		time = rtia.queryFederateTime()
		rtia.timeAdvanceRequest(time)
		while (mya.advanceTime == False):
			rtia.tick()
		mya.advanceTime = False
		#################################
except KeyboardInterrupt:
    print "\033[0;0m Keyboard Interrupt"

mya.terminate()

rtia.resignFederationExecution(hla.rti.ResignAction.DeleteObjectsAndReleaseAttributes)

print("Done.")
