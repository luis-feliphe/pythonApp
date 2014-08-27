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
		self.advanceTime = False
		self.isRegistered = False
		self.isAnnounced = False
		self.isReady = False
		self.isConstrained = False
		self.isRegulating = False
		#configuring data to be received
		self.classHandle = rtia.getObjectClassHandle("SampleClass")
		self.textAttributeHandle = rtia.getAttributeHandle("TextAttribute", self.classHandle)
		self.structAttributeHandle = rtia.getAttributeHandle("StructAttribute", self.classHandle)
		self.fomAttributeHandle = rtia.getAttributeHandle("FOMAttribute", self.classHandle)

		rtia.subscribeObjectClassAttributes(self.classHandle,[self.textAttributeHandle, self.structAttributeHandle, self.fomAttributeHandle])

	def reflectAttributeValues(self, object, attributes, tag, order, transport, time=None, retraction=None):
		print ("foi chamado")
		if self.textAttributeHandle in attributes:
			print("REFLECT", attributes[self.textAttributeHandle])

		if self.structAttributeHandle in attributes:
			structValue = struct.unpack('hhl', attributes[self.structAttributeHandle])
			print("REFLECT", structValue)

		if self.fomAttributeHandle in attributes:
			fomValue, size = fom.HLAfloat32BE.unpack(attributes[self.fomAttributeHandle])
			print("REFLECT", fomValue)


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
		rtia.requestObjectAttributeValueUpdate(object, [self.textAttributeHandle, self.structAttributeHandle, self.fomAttributeHandle])
	def timeAdvanceGrant (self, time):
		self.advanceTime = True



print("Create ambassador")
rtia = hla.rti.RTIAmbassador()

mya = MyAmbassador()

########## CRIA FEDERACAO ########



try:
    rtia.createFederationExecution("uav", "uav.fed")
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
