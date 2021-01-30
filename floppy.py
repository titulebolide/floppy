##Imports initiaux
import RPi.GPIO as GPIO #Programme qui contrôle la position de la plaquette de lecture des lecteurs de disquettes lorsqu'ils jouent de la musique En théorie, pour les musiques de moins de 40 000 Hz /!\ à l'échantillonnage!
import time
import os
import math
from threading import Thread
from mido import midifiles
GPIO.setwarnings(False)

##Structure des branchements
floppypin = [(0,12,16),(1,18,22)] #liste des couples, channel(quel est le channel joué sur ce floppy), pindir, pinstep pour tous les floppy connectés

##Définition du thread floppy. Fait une note lorsque self.playnote = True
class floppy(Thread):
	def __init__(self, pindir, pinstep):
		Thread.__init__(self)
		#Allumage des GPIO demandés
		try:
			GPIO.setmode(GPIO.BOARD)
			GPIO.setup(pindir, GPIO.OUT, initial=GPIO.LOW) #Le pin pindir est connecté à la broche 18 du floppy, /DIR
			GPIO.setup(pinstep, GPIO.OUT, initial=GPIO.LOW) #Le pin pinstep est connecté à la broche 20 du floppy, /STEP
		except RuntimeError:
			print("Il est mort, Jim! Problème de connection aux GPIOs. Réessayez avec sudo ")
		##Calibrage du lecteur:
		for _ in range(90):
			GPIO.output(pinstep, GPIO.HIGH)
			time.sleep(.0)
			GPIO.output(pinstep, GPIO.LOW)
			time.sleep(.01)
		GPIO.output(pindir, GPIO.HIGH)
		self.pindir = pindir
		self.pinstep = pinstep
		self.playnote = False #attribut qui est mis à False lorsqu'il faut arrêter de jouer la note
		self.period = 0.005 #période de la note à jouer (hauteur)
		self.kill = False #si mis à True, alors le thread est arrêté

	def run(self):
		while not self.kill:
			if self.playnote:
				GPIO.output(self.pinstep, GPIO.HIGH)
				time.sleep(.00)
				GPIO.output(self.pinstep, GPIO.LOW)
				GPIO.output(self.pindir, not GPIO.input(self.pindir))
			time.sleep(self.period) #arret entre un top et un autre


def run():
	print("""---------------------------------------------------------\nMusical Floppy Driver. GPIO 12 : /DIR ; GPIO 16 : /STEP\n---------------------------------------------------------""")
	print("Quel fichier utiliser? (donner le chemin et l'extension, fichier actuel: {0} )".format(os.getcwd()))

	##Ouverture du fichier
	while 1:
		try:
			fil = input("")
			l=list(midifiles.MidiFile(f))
			break
		except:
	                print("Mauvaise entrée")

	##Allumage et calibration des lecteurs
	print("[Initialisation des lecteurs]")
	floppylist = [] #liste des objets floppy
	for _, pindir, pinstep in floppypin:
		floppylist.append(floppy(pindir, pinstep))
		floppylist[-1].start()

	##Mainloop
	print("[Marche]")
	for event in l:
	        if not event.type in ('note_on', 'note_off'):
	                if event.type == 'set_tempo':
	                        tempo = event.tempo
	                continue
	        pause, channel, isup, note = event.time, event.channel, event.type == 'note_on', event.note
	        periode = 1/(32.7*2**((note-36)/12))
	        print(pause, isup, round(periode, 7))
	        time.sleep(pause)
	        nofloppy = [p[0] for p in floppypin].index(channel)
	        f = floppylist[nofloppy]
	        currentstate = f.playnote
	        if isup and not currentstate:
	                f.period = periode
	                f.playnote = True
	        elif not isup and currentstate and periode==f.period:
	                f.playnote = False
	for f in floppylist:
	        f.kill = True
	        f.join()
	print("[Terminé]")


if __name__=="__main__":
	run()
