#include <iostream>
#include <cstdlib>
#include <thread>
#include <chrono>
#include <math.h>
#include <unistd.h>
#include "rtmidi/RtMidi.h"
#include <wiringPi.h>

using namespace std;

int transpose = 27;
int max_note = 120;

class Floppy {

public:

	bool m_play  = false;
	long m_period = 5000;
	int m_note = 0;
	bool m_kill = false;


	void startNote(int note) {
		m_play = true;
		double periode = 1000000. / (32.7 * pow(2.,((note - transpose) / 12.)));
		m_period = (int)periode;
		m_note = note;
	}

	void stopNote() {
		m_play = false;
	}

	void run() {
		int dir = 0;
		while (!m_kill) {
			if (m_play) {
				auto start = chrono::high_resolution_clock::now();
				digitalWrite(4, HIGH);
				usleep(m_period*1/5);
				digitalWrite(4, LOW);
				if (dir == 1) {
					digitalWrite(1, HIGH);
				} else {
					digitalWrite(1, LOW);
				}
				dir = 1 - dir;
				auto elapsed = chrono::high_resolution_clock::now() - start;
				double el = chrono::duration_cast<chrono::microseconds>(elapsed).count();
				if (el > m_period*4/5) {
					cout << "You play too high!" << endl;
				} else {
					usleep(m_period*4/5 - el);
				}
			}
		}
	}
};

Floppy *f = new Floppy();

void callback (double timeStamp, std::vector< unsigned char > *msg, void *userData) {
	int chan = (*msg)[0] & 0xf;
	int note =  (*msg)[1];
	int velocity =  (*msg)[2];

	if (note < max_note && velocity==0 && f->m_note==note) {
		f->stopNote();
	} else if (note < max_note && velocity>0) {
		f->startNote(note);
	}
	cout << to_string(chan) << "," << to_string(note) << "," << to_string(velocity) << endl;
}


int main() {

	wiringPiSetup();
	pinMode(1, OUTPUT);
	pinMode(4, OUTPUT);

	std::thread th(&Floppy::run, f);

	RtMidiIn *midiin = new RtMidiIn();
	midiin->openPort(1);
	midiin->setCallback(callback);

	while(1) {
		delay(1000);
	}

	return 0;
}
