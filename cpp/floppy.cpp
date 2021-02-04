#include <iostream>
#include <cstdlib>
#include <thread>
#include <chrono>
#include <math.h>
#include <unistd.h>
#include "rtmidi/RtMidi.h"
#include <wiringPi.h>

using namespace std;

class Floppy
{
public:
  bool m_play  = false;
  long m_period = 5000;
  int m_note = 0;
  bool m_kill = false;

  void startNote(int note) {
    m_play = true;
    double periode = 1 / (32.7 * pow(2.,((note - 27.) / 12.)))*1000000;
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
        long long el = chrono::duration_cast<chrono::microseconds>(elapsed).count();
	if (el > m_period*4/5){
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
  int msgtype = (*msg)[0] & 0xf0;
  int note =  (*msg)[1];
  int velocity =  (*msg)[2];

  if (note < 69 && velocity==0 && f->m_note==note){
     f->stopNote();
  } else if (note < 69 && velocity>0) {
     f->startNote(note);
  }
  cout << to_string(msgtype) << "," << to_string(chan) << "," << to_string(note) << "," << to_string(velocity) << endl;
}


int main()
{

  wiringPiSetup();                        // Setup the library
	pinMode(1, OUTPUT);             // Configure GPIO0 as an output
	pinMode(4, OUTPUT);             // Configure GPIO1 as an input

  std::thread th(&Floppy::run, f);

  RtMidiIn  *midiin = 0;
  RtMidiOut *midiout = 0;
  // RtMidiIn constructor
  try {
    midiin = new RtMidiIn();
  }
  catch ( RtMidiError &error ) {
    error.printMessage();
    exit( EXIT_FAILURE );
  }
  // Check inputs.
  unsigned int nPorts = midiin->getPortCount();
  cout << "\nThere are " << nPorts << " MIDI input sources available.\n";
  string portName;
  for ( unsigned int i=0; i<nPorts; i++ ) {
    try {
      portName = midiin->getPortName(i);
    }
    catch ( RtMidiError &error ) {
      error.printMessage();
      //goto cleanup;
    }
    cout << "  Input Port #" << i << ": " << portName << '\n';
  }
  // Clean up


  midiin->openPort(1);
  midiin->setCallback(callback);

  std::vector<unsigned char> message;

  while(1) {
    /*
    double stamp = midiin->getMessage( &message );
    int nBytes = message.size();
    if (nBytes > 0) {
      cout << "kjlh" << endl;
    }
    */
    usleep(100);
  }

  return 0;
}
