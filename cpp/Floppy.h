#include <thread>

class Floppy
{
  public:

	bool m_play  = false;
	long m_period = 5000;
	int m_note = 0;
	bool m_kill = false;
  int m_stepPin;
  int m_dirPin;

  Floppy(int stepPin, int dirPin);
	void startNote(int note);
	void stopNote();
  void run();
	std::thread start();
};
