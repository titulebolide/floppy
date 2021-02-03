# coding: utf-8

# Imports initiaux
import RPi.GPIO as GPIO  # Programme qui controle la position de la plaquette de lecture des lecteurs de disquettes lorsqu'ils jouent de la musique En théorie, pour les musiques de moins de 40 000 Hz /!\ à l'échantillonnage!
import time
import os
import math
import click
from threading import Thread
from mido import midifiles
GPIO.setwarnings(False)

# Structure des branchements
# liste des couples, channel(quel est le channel joué sur ce floppy), pindir, pinstep pour tous les floppy connectés
floppypin = [(0, 12, 16)]
floppylist=[]
# Définition du thread floppy. Fait une note lorsque self.playnote = True


class floppy(Thread):
    def __init__(self, pindir, pinstep):
        Thread.__init__(self)
        # Allumage des GPIO demandés
        try:
            GPIO.setmode(GPIO.BOARD)
            # Le pin pindir est connecté à la broche 18 du floppy, /DIR
            GPIO.setup(pindir, GPIO.OUT, initial=GPIO.LOW)
            # Le pin pinstep est connecté à la broche 20 du floppy, /STEP
            GPIO.setup(pinstep, GPIO.OUT, initial=GPIO.LOW)
        except RuntimeError:
            print(
                "Il est mort, Jim! Problème de connection aux GPIOs. Réessayez avec sudo ")
        # Calibrage du lecteur:
        for _ in range(90):
            GPIO.output(pinstep, GPIO.HIGH)
            time.sleep(.0)
            GPIO.output(pinstep, GPIO.LOW)
            time.sleep(.01)
        GPIO.output(pindir, GPIO.HIGH)
        self.pindir = pindir
        self.pinstep = pinstep
        # attribut qui est mis à False lorsqu'il faut arrêter de jouer la note
        self.playnote = False
        self.period = 0.005  # période de la note à jouer (hauteur)
        self.kill = False  # si mis à True, alors le thread est arrêté

    def run(self):
        while not self.kill:
            if self.playnote:
                GPIO.output(self.pinstep, GPIO.HIGH)
                time.sleep(.00)
                GPIO.output(self.pinstep, GPIO.LOW)
                GPIO.output(self.pindir, not GPIO.input(self.pindir))
            time.sleep(self.period)  # arret entre un top et un autre


@click.command()
@click.option("--transpose", default=3)
@click.argument('filename')
def run(transpose, filename):
    global floppylist
    # Ouverture du fichier
    l = list(midifiles.MidiFile(filename))

    # Allumage et calibration des lecteurs
    print("[Initialisation des lecteurs]")
    for _, pindir, pinstep in floppypin:
        floppylist.append(floppy(pindir, pinstep))
        floppylist[-1].start()

    # Mainloop
    print("[Marche]")
    for event in l:
        if not event.type in ('note_on', 'note_off'):
            if event.type == 'set_tempo':
                tempo = event.tempo
            continue
        periode = 1 / (32.7 * 2**((event.note - 12*transpose) / 12))
        print(round(event.time,3), event.type, round(event.note, 3))
        time.sleep(event.time)
        nofloppy = [p[0] for p in floppypin].index(event.channel)
        f = floppylist[nofloppy]
        f.period = periode
        if event.type == 'note_on':
            f.playnote = True
        else:
            f.playnote = False
    kill()


def kill():
    global floppylist
    for f in floppylist:
        f.kill = True
        f.join()
    print("[Terminé]")


if __name__ == "__main__":
    try:
        run(standalone_mode=False)
    except click.exceptions.Abort:
        kill()
