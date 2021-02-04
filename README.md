# [WIP] Flop-Pi
Play music on floppy drivers with a raspberry pi, written both in Python and C++

## Installation
In order not to have the script running as superuser, add yourself to the `sudo` and `gpio` groups:
```bash
sudo usermod -a -G audio $USER
sudo usermod -a -G gpio $USER
```
Then log off, and log back.
Then install the needed python packages:
```bash
pip3 install --user -r requirements.txt
```

