#include <iostream>
#include <cstdlib>
#include <chrono>
#include <algorithm>
#include <math.h>
#include <unistd.h>
#include "rtmidi/RtMidi.h"
#include <thread>
#include <wiringPi.h>
#include <iterator>
#include "Floppy.h"

using namespace std;


vector<Floppy> floppies = {
	Floppy(1,4),
	Floppy(5,6),
	Floppy(7,0)
};

vector<int> notes(floppies.size(), 0);

void callback (double timeStamp, vector< unsigned char > *msg, void *userData) {
	int type = (*msg)[0];
	int note =  (*msg)[1];
	int velocity =  (*msg)[2];

	if ((type == 144 && velocity == 0) || type == 128) {
		for (size_t nofloppy = 0; nofloppy < floppies.size(); nofloppy++) {
			if (notes[nofloppy] == note) { // note is currently played
				floppies[nofloppy].stopNote();
				notes[nofloppy] = 0;
				break; //there should not be any other playing floppy
			}
		}
	} else if (type == 144) {
		for (size_t nofloppy = 0; nofloppy < floppies.size(); nofloppy++) {
			if (notes[nofloppy] == 0) {
				floppies[nofloppy].startNote(note);
				notes[nofloppy] = note;
				break;
			}
		}
	}

	cout << to_string(type) << "," << to_string(note) << "," << to_string(velocity) << endl;
}


int main() {

	wiringPiSetup();

	vector<thread> ths;

	for (size_t i = 0; i < floppies.size(); i++)
	{
		Floppy &floppy = floppies[i];
		ths.push_back(floppy.start());
	}

	RtMidiIn *midiin = new RtMidiIn();
	midiin->openPort(1);
	midiin->setCallback(callback);

	for (size_t i = 0; i < ths.size(); i++)
	{
		ths[i].join();
	}

	return 0;
}
