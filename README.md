# 3D-Printer-Failure-Detection
*This was a university (Hons) project and may not be updated.

Overview:
Computer-Vision based 3D Printer Failure Detection in OpenCV, Python. Designed to work with a basic USB webcam placed directly in front of an FDM/FFF printer, to alert the user of a print failure (not stop the printer). 

Accuracy: 
| ~80% (with colourful plastic, in bed detachment detection).
| Does not work with grey scale colours.

2 versions:
| Windows.
| Linux (min specs: Raspberry Pi 3).

Needed Packages:
| opencv-contrib-python (4.4.0.XX) :- manual detection incompatibility with 4.5 versions
| gpiozero (1.5.1) :- Windows version includes it but the code can be removed in "failureAlert.py"
| Pillow (8.0.1)
| numpy (1.19.4)

