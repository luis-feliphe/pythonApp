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
		self.classHandle = rtia.getObjectClassHandle("SampleClass")

		self.textAttributeHandle = rtia.getAttributeHandle("TextAttribute", self.classHandle)
		self.structAttributeHandle = rtia.getAttributeHandle("StructAttribute", self.classHandle)
		self.fomAttributeHandle = rtia.getAttributeHandle("FOMAttribute", self.classHandle)

		rtia.publishObjectClass(self.classHandle,[self.textAttributeHandle, self.structAttributeHandle, self.fomAttributeHandle])
		self.myObject = rtia.registerObjectInstance(self.classHandle, "HAF")

	def terminate(self):
		rtia.deleteObjectInstance(self.myObject, "HAF")

	# RTI callbacks
	def startRegistrationForObjectClass(*params):
		pass

	def provideAttributeValueUpdate(*params):
		pass

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


print "\n --------x  Starting Python Aplication   x---------"
print ("Create ambassador")
rtia = hla.rti.RTIAmbassador()


####### Try Create a Federation ##############
try:
    rtia.createFederationExecution("uav", "uav.fed")
    log("Federation created.\n")
except hla.rti.FederationExecutionAlreadyExists:
    log("Federation already exists.\n")




####### Join into a Federation ###############
mya = MyAmbassador()
rtia.joinFederationExecution("uav-send", "uav", mya)

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
    a= 3.14
    while(1):
	########## Main Loop ###########

        a = a + 1.0
        rtia.updateAttributeValues(mya.myObject, {mya.textAttributeHandle:"TESTANDO   ", mya.structAttributeHandle:struct.pack('hhl', 1, 2, 3), mya.fomAttributeHandle:fom.HLAfloat32BE.pack(a)},"update")
	#print "tick"
	#rtia.tick()
        rtia.tick(1.0, 1.0)
	
	
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
