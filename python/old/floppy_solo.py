# -*- coding: utf8 -*-
import RPi.GPIO as GPIO #Programme qui contrôle la position de la plaquette de lecture des lecteurs de disquettes lorsqu'ils jouent de la musique En théorie, pour les musiques de moins de 40 000 Hz /!\ à l'échantillonnage!
import time
import os
import math
GPIO.setwarnings(False)
try:
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(12, GPIO.OUT, initial=GPIO.HIGH) #Le pin 12 est connecté à la broche 18 du floppy, /DIR
	GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW) #Le pin 16 est connecté à la broche 20 du floppy, /STEP
except RuntimeError:
	print("""Il est mort, Jim! Problème de connection aux GPIOs. Réessayez avec "sudo" """)
print("""---Musical Floppy Driver. GPIO 12 : /DIR ; GPIO 16 : /STEP---\n""")
print("Quel fichier utiliser? (donner le chemin et l'extension, fichier actuel: {0} )".format(os.getcwd()))
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
freq = 0 #Fréquence de la note, et durée de la periode
freq = float(freq)
nbtop = 0 #comptabilise le nb de tops envoyés a la disquette, depuis le dernier changement de sens de sa platine
precval = 1 #si égal a 1, alors la platine se déplace vers l'avant dc GPIO 12 (/DIR) = 1
dur = 0 #durée d'une note en tops
dur0 = 0 #variable annexe pour rapidifier
pause = 0 #durée du stop entre deux notes
pause0 = 0 #variable annexe
nbtour = 0 #nb de tour de notre fonction, à comparer avec dur
l=f.readlines()
spd = float(l[0]) #on aquiert le facteur de vitesse qui est en ligne 1
spdnote = 300*spd #durée d'une note
spdpause = 289 *spd #durée de la pause
i=1 #itérateur, qui permet de nous repérer dans la liste l
i0 = 2 #var annexe
j = 6 #emplacement de l'espace après l'info de dur, permet de savoir le décalage de la ligne si l'info exède 3 chiffres
note=0 #n° en demi tons en partant de 0 du do gamme 0 de la note jouée
note = float(note)
note1=0 #variable d'extension du deuxieme chiffre de note, qui peut etre string
note0 = 0 #variable d'extension
dur=0 #durée en UA de la note
tall=len(l)
print("[Calibrage]")
while nbtour <= 160 : #Calibrage de la platine
	GPIO.output(16, GPIO.HIGH)
	time.sleep(.00)
	GPIO.output(16, GPIO.LOW)
	nbtop += 1
	nbtour += 1
	if nbtop == 80:
		nbtop = 0
		if precval == 1:
			GPIO.output(12, GPIO.LOW)
			precval = 0
		else:
			GPIO.output(12, GPIO.HIGH)
			precval = 1
	time.sleep(.01)
time.sleep(1)
print("[Marche]")
for i in range(2,tall,2): #on commence a la ligne 3 du doc car la ligne 1 est la vitesse, et la deux le off de la prmière note(donc inutile)
	dur0 = l[i][3]
	j = 3
	while str(dur0) != " ":
		j+=1
		dur0 = l[i][j]
	if j <= 7:
		dur = int(l[i][3]+l[i][4]+l[i][5]+l[i][6])
	elif j == 8:
		dur = int(l[i][3]+l[i][4]+l[i][5]+l[i][6]+l[i][7])
	else:
		print ("Erreur, fichier invalide, revoir la longueur des notes")
	if j == 7:
		j = 1
	elif j == 8 :
		j = 2
	else:
		j = 0
	note0 = int(l[i][14+j])
	note1 = l[i][15+j]
	try:
		note = 16*note0+int(note1)
	except ValueError: #car c'est de l'hexa, et on ne peut faire int("A")
		if note1=="A":
			note=16*note0+10
		elif note1=="B":
			note=16*note0+11
		elif note1=="C":
			note=16*note0+12
		elif note1=="D":
			note=16*note0+13
		elif note1=="E":
			note=16*note0+14
		elif note1=="F":
			note=16*note0+15
	print(note,dur)
	note = float(note - 48) #note est un  int, et bloque le calcul suivant qui est flottant, et on la réajuste, pour éviter des notes trop aigües
	freq = 32.7*pow(2,(note/12)) #on détermine en calculant la fréquence de la note en fonction de sa valeur
	freq = 1/freq
	dur = (dur/freq)/spdnote #on fait ce calcul afin que quelque soit la fréquence, la durée réelle d'une note soit proportionelle a dur on divise ensuite par cent, sinon la valeur de dur est trop grande
	nbtour = 0
	while nbtour <= dur :
		GPIO.output(16, GPIO.HIGH)
		time.sleep(.00)
		GPIO.output(16, GPIO.LOW)
		nbtop += 1
		nbtour += 1
		if nbtop == 80:
			nbtop = 0
			if precval == 1:
				GPIO.output(12, GPIO.LOW)
				precval = 0
			else:
				GPIO.output(12, GPIO.HIGH)
				precval = 1
		time.sleep(freq) #arret entre un top et un autre
	i0 = i+1
	if i0 != tall:
		pause0 = l[i][3]
		j = 3
		while str(pause0) != " ":
			j+=1
			pause0 = l[i0][j]
		if j <= 7:
			pause = int(l[i0][3]+l[i0][4]+l[i0][5]+l[i0][6])
		elif j == 8:
			pause = int(l[i0][3]+l[i0][4]+l[i0][5]+l[i0][6]+l[i0][7])
		else:
			print ("Erreur, fichier invalide, revoir la longueur des notes")
		print(pause)
	pause = float(pause)
	pause=(pause/spdpause)#on retravaille pause, car les valeurs données ne conviennent pas 375-1000
	time.sleep(pause) #arret entre deux notes
f.close()
print("[Terminé]")
