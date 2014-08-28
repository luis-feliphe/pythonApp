#!/usr/bin/env python
# Requires PyHLA, see http://www.nongnu.org/certi/PyHLA
import hla.rti
import hla.omt as fom

import struct
def log (valor):
	print str(valor)
class MyAmbassador(hla.rti.FederateAmbassador):
	def initialize(self):
		#Variables
		self.time = 0
		self.advanceTime = False
		self.isRegistered = False
		self.isAnnounced = False
		self.isReady = False
		self.isConstrained = False
		self.isRegulating = False
		######## Configurando objetos a serem recebidos ##############

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

		rtia.subscribeObjectClassAttributes(self.classHandle,[self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
		##############################################################

	def reflectAttributeValues(self, object, attributes, tag, order, transport, time=None, retraction=None):
		if self.batteryHandle in attributes:
			#print("REFLECT", attributes[self.batteryHandle])
			#print("Alguma coisa nao esta certa aqui")
			pass

		if self.temperatureHandle in attributes:
			#print("REFLECT", attributes[self.temperatureHandle])
			valor = attributes[self.temperatureHandle]
			"""valor =  valor.split(":")[1]
			valor =  valor.replace("\"", "")
			valor =  valor.replace("\\", "")
			valor =  valor.replace(">", "")
			valor =  valor.replace("<", "")
			x, y  = valor.split(";")
			import time
			time.sleep(1)
			print ("valor x : " + str (x) + " valor y : " + str (y))"""
			print ("Received value: ", valor)
			if (int (x) != 0):
				#TODO Do something
				#self.ser.write("<"+ str(x)+ ":" + str( y )+ ">")
				#print ("dados enviados ao Arduino")
				pass


		if self.sensor1Handle in attributes:
			#print("REFLECT", attributes[self.sensor1Handle])
			pass#print("REFLECT", attributes[self.sensor1Handle])




	def terminate(self):
		rtia.deleteObjectInstance(self.myObject, "HAF")

	# RTI callbacks
	def startRegistrationForObjectClass(*params):
		print("START", params)

	def provideAttributeValueUpdate(*params):
		print("PROVIDE UAV", params)

	def synchronizationPointRegistrationSucceeded(self, label):
		self.isRegistered = True
		print ("MyAmbassador: Registration Point Succeeded")

	def announceSynchronizationPoint(self, label, tag):
		self.isAnnounced = True
		print ("MyAmbassador: Announce Synchronization Point")

	def federationSynchronized (self,  label):
		self.isReady = True
		print ("MyAmbassador: Ready to run ")

	def timeConstrainedEnabled (self, time):
		self.isConstrained = True

	def timeRegulationEnabled (self, time): 
		self.isRegulating = True

	def discoverObjectInstance(self, object, objectclass, name):
		print("DISCOVER", name)
		rtia.requestObjectAttributeValueUpdate(object,[self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
	def timeAdvanceGrant (self, time):
		self.advanceTime = True



print("Create ambassador")
rtia = hla.rti.RTIAmbassador()

mya = MyAmbassador()

########## CRIA FEDERACAO ########



try:
    rtia.createFederationExecution("uav", "PyhlaToPtolemy.fed")
    log("Federation created.\n")
except hla.rti.FederationExecutionAlreadyExists:
    log("Federation already exists.\n")




####### Join into a Federation ###############
mya = MyAmbassador()
rtia.joinFederationExecution("uav-recv", "uav", mya)

mya.initialize()


log("inicialized!\n")


######### Announce Synchronization Point ######


label = "ReadyToRun"
tag =  bytes ("hi!")
rtia.registerFederationSynchronizationPoint(label, tag)
print("Synchronization Point Register!")

while  (mya.isRegistered == False or mya.isAnnounced == False):
	rtia.tick()
print "tick"

####### Esperando outros Federados ############
x = input ("Waiting others federators\n")

#######Archieve Synchronized Point  ###########

rtia.synchronizationPointAchieved("ReadyToRun")
while (mya.isReady == False):
	rtia.tick()
print ("MyAmbassador : Is Ready to run ")

##### Enable Time Policy #####################
currentTime =rtia.queryFederateTime()
lookAhead = rtia.queryLookahead()
rtia.enableTimeRegulation(currentTime, lookAhead)

while (mya.isRegulating == False):
	rtia.tick()

rtia.enableTimeConstrained()
while (mya.isConstrained == False):
	rtia.tick()
print ("MyAmbassador: Time is Regulating and is Constrained")
############################################

try:
    while(1):
	########## Main Loop #############

        rtia.tick(1.0, 1.0)

	#######  Time Management  ########
	time = rtia.queryFederateTime()
	rtia.timeAdvanceRequest(time)
	while (mya.advanceTime == False):
		rtia.tick()
	mya.advanceTime = False
	##################################
except KeyboardInterrupt:
    pass

mya.terminate()

rtia.resignFederationExecution(hla.rti.ResignAction.DeleteObjectsAndReleaseAttributes)

print("Done.")
