# Computer Vision based measuring app #
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

## Instructions for Use

### Run
To start the app, run the following startscript:
```
./measure.sh

```
The script is structured in the following format:
```
python3 measurement.py -p <string Image-path> -s <float Scale-Factor> -t <string type("numpy","csv","tsv")> -c <int Space separated RGB code>

```
### Measuring
Press the Measure button to start measuring distances.
  - Once in measure mode, select points on the displayed image using mouse
    clicks. This highlights the hole closest to the user’s choice. On choosing the
    second point, a line is drawn from start(Center of hole of start point) to goal
    (Center of hole of goal point) with the length of the line specified.
  - Any clicks beyond that over-write the second point.
  - The Clear button clears all the data and takes the user out of measure mode.
  - The 'Generate' button saves all the points selected by the user in one session in the appropriate format.
 
## Results
![Working GIF](https://github.com/Vram97/Calibration_App_For_Vision_Guided_Robots/blob/master/Peek%202023-03-05%2021-31.gif)
