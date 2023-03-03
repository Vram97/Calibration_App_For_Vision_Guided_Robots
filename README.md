# Calibration App for Vision Guided Robots
![Main image](https://ros-planning.github.io/moveit_tutorials/_images/hand_eye_calibration_demo.jpg)

## Introduction
This a computer vision based calibration app whose applications range from measurement of dimensions of critical parts to robotic hand-eye calibration.

## Setup
The following libraries and softwares need to be installed to run the code:
- Python3
- OpenCV
- Numpy
- PIL
- TKinter
- OptParse
- Math
- CSV

## Run
To start the app, run the following startscript:
```
./measure.sh

```
The script is structured in the following format:
```
python3 measurement.py -p <string Image-path> -s <float Scale-Factor> -t <string type("numpy","csv","tsv")> -c <int Space sepaerated RGB code>

```
## Results
