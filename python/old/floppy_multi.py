# -*- coding: utf8 -*-

##Imports initiaux
import RPi.GPIO as GPIO #Programme qui contrôle la position de la plaquette de lecture des lecteurs de disquettes lorsqu'ils jouent de la musique En théorie, pour les musiques de moins de 40 000 Hz /!\ à l'échantillonnage!
import time
import os
import math
from threading import Thread
GPIO.setwarnings(False)

def read(line): #decode une ligne et renvoie les élements clés.
	pause = int(line[3:7])
	if line[6] == " ":
		dec = 0
	else:
		dec = 1
	isup = (line[12+dec] == "+")
	channel = int(line[9+dec:11+dec])
	note = int(line[14+dec:16+dec],16) - 36
	periode = 1/(32.7*2**(note/12))
	return pause, channel, isup, periode	

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
                			
		

print("""---------------------------------------------------------\nMusical Floppy Driver. GPIO 12 : /DIR ; GPIO 16 : /STEP\n---------------------------------------------------------""")
print("Quel fichier utiliser? (donner le chemin et l'extension, fichier actuel: {0} )".format(os.getcwd()))

##Ouverture du fichier
while 1:
	try:
		fil = input("")
		f=open(fil,"r")
		break
	except IOError:
		print("Aucun fichier ne correspond au chemin ou au nom rentré")
	except NameError:
		print("Mettez des guillemets")
	except TypeError:
		print("Une suite de caractères est attendue")
	except SyntaxError:
		print("La syntaxe rentrée est erronée")

##Définition des variables
floppypin = [(1,12,16),(2,18,22)] #liste des couples, channel(quel est le channel joué sur ce floppy), pindir, pinstep pour tous les floppy connectés
dur = 0 #durée d'une note en tops
dur0 = 0 #variable annexe pour rapidifier
pause = 0 #durée du stop entre deux notes
pause0 = 0 #variable annexe
nbtour = 0 #nb de tour de notre fonction, à comparer avec dur
l=f.readlines()
f.close()
spd = float(l[0]) #on aquiert le facteur de vitesse qui est en ligne 1
spdnote = 300*spd #durée d'une note
i=1 #itérateur, qui permet de nous repérer dans la liste l
i0 = 2 #var annexe
j = 6 #emplacement de l'espace après l'info de dur, permet de savoir le décalage de la ligne si l'info exède 3 chiffres
note = 0. #n° en demi tons en partant de 0 du do gamme 0 de la note jouée
note1=0 #variable d'extension du deuxieme chiffre de note, qui peut etre string
note0 = 0 #variable d'extension
dur=0 #durée en UA de la note
tall=len(l)

##Allumage et calibration des lecteurs
print("[Initialisation des lecteurs]")
floppylist = [] #liste des objets floppy
for _, pindir, pinstep in floppypin:
	floppylist.append(floppy(pindir, pinstep))
	floppylist[-1].start()

##Mainloop
print("[Marche]")
for line in l[1:]:
	if not("+" in line or "-" in line[12:14]): #si la ligne que l'on regarde n'est pas une jouer note, alors on passe directement au prochain tour de boucle
		continue
	pause, channel, isup, periode = read(line)
	print(pause, isup, round(periode, 7))
	time.sleep(pause/spdnote)
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
