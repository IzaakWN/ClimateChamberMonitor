# ClimateChamberMonitor
Run and monitor a LabEvent climate chamber with python scripts using SIMPAC simserve commands.

## Installation
Clone this repository:
```
git clone https://github.com/IzaakWN/ClimateChamberMonitor ClimateChamberMonitor
```
And set the correct IP address of LabEvent in `chamber_commands.py`, e.g.
```
sed "s/ip = '[^']*'/ip = '130.60.164.144'/g" -i chamber_commands.py
```
Submodules are automatically included: `statsd` and Yoctopuce python libraries. Update to the latest version:
```
git submodule update --init --recursive
```

## Monitor
Monitor the climate chamber in a GUI window and write to a log file `monitor.dat` (csv format) with
```
python monitor.py
```
Run in batch mode (no GUI window, only write to log file) with the `-b` flag:
```
python monitor.py -b
```
The script stops until you close the window, or in batch mode, interrupt it with `CTRL + C`.
A maximum monitoring time in seconds can be set with the `-t` option.
Sampling rate of temperature reading can be set in seconds with the `-s` flag.

## Manual run
Run and monitor the climate chamber with a manual run to a given target temperature
```
python run_manual.py -T 18.0
```

## Program run
Run and monitor program specified by number via `-p` flag:
```
python run_program.py -p 2
```

