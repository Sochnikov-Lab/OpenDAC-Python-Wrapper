# OpenDAC-Python-Wrapper
Python wrapper and extended Arduino code for the serial controlled OpenDAC DAC-ADC.
Original Arduino sketch provided here: http://opendacs.com/dac-adc-homepage/dac-adc-code/
Our Lab: https://trello.com/b/DvzZh9hL/sochnikov-lab-nanoscale-imaging-uconn
You will need PyQt5 installed to make use of the GUI and PySerial to communicate with the hardware. It is suggested that you use
Anaconda. 

# Arduino Code:
We are adding some common functions and acquisition features that were missing in the original firmware (1,2,4 channel acquire / Sine output / DC output / ramp & readout) . To be documented later.

# Python Code:
The bare wrapper (opendacwrapper.py) and the ODAC object are used to facilitate communication with the OpenDAC DAC-ADC hardware. This can be used to write simple control scripts to possibly automate your measurement workflow. Additionally, we provide a graphical control interface for the most common functions. This object is still a WIP so changes will be made. To be documented later.
