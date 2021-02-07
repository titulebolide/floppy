#include <iostream>
#include <cstdlib>
#include <thread>
#include <chrono>
#include <math.h>
#include <unistd.h>
#include "rtmidi/RtMidi.h"
#include <wiringPi.h>
#include <thread>
#include "Floppy.h"

using namespace std;

Floppy::Floppy(int stepPin, int dirPin): m_stepPin(stepPin), m_dirPin(dirPin)
{}

void Floppy::startNote(int note) {
	cout << to_string(note) << endl;
	m_play = true;
	double periode = 1000000. / (32.7 * pow(2.,((note - 27) / 12.)));
	m_period = (int)periode;
	m_note = note;
}

void Floppy::stopNote() {
  m_play = false;
}

thread Floppy::start() {
	return thread([this]{this->run();});
}

void Floppy::run() {
	cout << to_string(m_stepPin) << endl;
	pinMode (m_stepPin, OUTPUT) ;
	pinMode (m_dirPin, OUTPUT) ;
	int dir = 0;
	while (!m_kill) {
		if (m_play) {
			auto start = chrono::high_resolution_clock::now();
			digitalWrite(m_stepPin, HIGH);
			usleep(m_period*1/5);
			digitalWrite(m_stepPin, LOW);
			if (dir == 1) {
				digitalWrite(m_dirPin, HIGH);
			} else {
				digitalWrite(m_dirPin, LOW);
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
