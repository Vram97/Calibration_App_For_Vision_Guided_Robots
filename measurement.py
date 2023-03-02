""" This is the code for a distance measurement app based on computer vision and user input 
Author: Shivaram Srikanth
Date: 02 - 19 - 2023 
"""

################## REQUIRED LIBRARIES #########################

import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from PIL import ImageTk, Image
from optparse import OptionParser
import math
import csv

################################################################
################## TUNABLE PARAMETERS ##########################

# Name of App
APP_NAME="Measurement App"

# Optimized based on existig size of image.
APP_SIZE= "680x420"           

# Background color
BACKGROUND_COLOR ="#2eb9cc"   

# Maximum area of detected contours
MAX_AREA=100

# Minimum distance for generating closest point.
THRESHOLD_DISTANCE=15 

# Canny Edge detection parameters (Optimized)
CANNY_MIN_THRESHOLD=80
CANNY_MAX_THRESHOLD=200

# Default parameters
DEFAULT_FILE_TYPE="numpy"
DEFAULT_SCALING_FACTOR=1
DEFAULT_COLOR=(255,255,0)
DEFAULT_IMAGE_PATH="grid.png"

#################################################################
################### REQUIRED CLASSES ############################
""" Class definitions for all classes used for the task"""

# Main viewer class of the app.
class ViewerFrame():

    def __init__(self,root,options):
        self.root=root                # Root frame of app  
        self.options=options          # User options
        self.internal_frame=internalFrame(self.root,self.options) # Internal frame that goes into the root frame

        self.setParam()
        
    # Sets all the parameters of the app. 
    def setParam(self):
        self.root.title(APP_NAME)
        self.root.geometry(APP_SIZE)
        self.root.resizable(False,False)
        self.root.config(bg=BACKGROUND_COLOR)

    # Function to call app loop from outside
    def mainloop(self):
        self.root.mainloop()

# Internal frame class that holds all buttons and image to be used for measurement.
class internalFrame():
    
    def __init__(self,root,options):

        self.color=options.pen_color          # Sets color for marking points and drawing lines.
        self.scale=options.scale_factor       # The pixel to distance factor as specified by the user.
        self.file_type=options.file_type           # The file type required by the user.

        self.img=Image.open(options.img_location)      # Holds the main image of the app.
        self.cv_image=cv2.cvtColor(np.array(self.img), cv2.COLOR_RGB2BGR)  # Holds the opencv image format required for operations
        self.imagetk=ImageTk.PhotoImage(self.img)       # Image in format supported by Tkinter

        self.frame=Frame(root).pack()                   # Main frame
        self.button_frame=Frame(self.frame)             # Frame to hold buttons.
        self.label=Label(self.frame,image=self.imagetk) # Label that holds the image.

        self.measure_btn=Button(self.button_frame, text="Measure",width=10,command=self.msr_handler)  # Measure button
        self.clear_btn=Button(self.button_frame,text="Clear",width=10,command=self.clear_handler)     # Clear button to reset to default measurements.
        self.dist=Label(self.button_frame,text="Distance: ",width=10)                                 # Label holding "Distance: " string
        self.distance_label=Label(self.button_frame,text="",width=10)                                 # Label to display distances
        self.file_generation=Button(self.button_frame,text="Generate Files",command=self.generate)    # Button to generate files as per the requirement of the user.

        self.state=stateChecker(self.cv_image)           # State variable to monitor the present state of the user's activities.

        self.setLayout()

    # Sets the layout of buttons in the button frame.
    def setLayout(self):
        
        # Setting a handler for left cliscks by mouse on the image to be measured.
        self.label.bind('<Button-1>',self.drawContour)
        self.label.pack()

        # Positioning buttons.
        self.measure_btn.grid(row=0,column=0,sticky=EW) 
        self.clear_btn.grid(row=0,column=1,sticky=EW)
        self.dist.grid(row=1,column=0,sticky=EW,pady=5)
        self.distance_label.grid(row=1,column=1,sticky=EW,pady=5)
        self.file_generation.grid(row=0,column=3,pady=5)
        self.button_frame.pack()

    ###################################################
        """ Button handlers """

    # Handler function for measure mode
    def msr_handler(self):
        self.state.measure_mode=True

    # Handler function for clear button
    def clear_handler(self):
        self.state.measure_mode=False           # Exiting measure mode.

        #Resetting states
        self.state.x1=None
        self.state.y1=None
        self.state.x2=None
        self.state.y2=None
        self.state.visited=[]
        self.label.imgtk=self.imagetk
        self.label.configure(image=self.imagetk)
        self.label.pack()

    # Generate files as required by the user.
    def generate(self):

        # Numpy file generation
        if(self.file_type=="numpy"):
            np.save("files.npy",np.array(self.state.visited))
            print(" Numpy file was generated succesfully! ")

        # CSV file generation
        elif(self.file_type=="csv"):
            count=1
            with open('files.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Serial No","X coordinate","Y coordinate"])

                for i in self.state.visited:
                    writer.writerow([count,i[0]*self.scale,i[1]*self.scale])
                    count+=1
            print(" CSV file generated succesfully! ")
            
        # TSV file generation
        elif(self.file_type=="tsv"):
            
            with open('output.tsv', 'w', newline='') as f_output:
                tsv_output = csv.writer(f_output, delimiter='\t')
                for i in self.state.visited:

                    tsv_output.writerow((i[0]*self.scale,i[1]*self.scale))
            print("TSV file generated successfully! ")


        else:
            print(" Unrecognized file type! Defaulting to Numpy format .....")
            np.save("files.npy",np.array((i[0]*self.scale,i[1]*self.scale) for i in self.state.visited))

    ####################################################
    """ All draw functions needed for the task. """

    # Contour drawing app method.
    def drawContour(self,evt):
        """ This function draws a contour around the hole that is closest to the user's input."""

        # Checking if the user is in measure mode.
        if(self.state.measure_mode==True):

            # Obtaining the centre of the hole closest to the user's click. 
            val=self.state.getClosest(int(evt.x),int(evt.y))

            # Checking if the user's clicks are close to any holes.
            if(val!=(None,None)):

                # Checking if user is clicking his/her second hole.
                if(self.state.x2!=None):

                    self.drawLine()     # Connecting two points

                # First click.
                else:
                    new_image=self.cv_image.copy()

                    # Drawing contour
                    cv2.drawContours(new_image, self.state.cnt_dict[(val[0],val[1])], -1, self.color, 2)

                    # Conversion back to tkinter format.
                    im_rgb = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
                    imgtk=ImageTk.PhotoImage(image=Image.fromarray(im_rgb))

                    # Updating the image on the frame holding the image.
                    self.label.imgtk=imgtk
                    self.label.configure(image=imgtk) 
                    self.label.pack()

    # Line draawing method that is used once two points are picked by the user.
    def drawLine(self):

        # Drawing a line connecting two points.
        new_image=self.cv_image.copy()
        new_image=cv2.line(new_image,(self.state.x1,self.state.y1),(self.state.x2,self.state.y2),self.color, 1)

        # Conversion back to image format supported by Tkinter.
        im_rgb = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
        imgtk=ImageTk.PhotoImage(image=Image.fromarray(im_rgb))

        # Updating the frame holding the image.
        self.label.imgtk=imgtk
        self.label.configure(image=imgtk) 

        # Updating the length of the line.
        self.distance_label['text']=str(round(self.state.getDistance() * self.scale,4))
        self.button_frame.pack()

######################################################################
""" State class that monitors the user's activity in the app."""

class stateChecker():
    def __init__(self,img) -> None:
        self.cnt_dict={}              # Dictionary storing the coordinates of hole centres and their corresponding contour.
        self.measure_mode=False       # Measuring mode

        # Initializing the 1st and 2nd centres specified by the user.
        self.x1=None
        self.y1=None
        self.x2=None
        self.y2=None
        self.closest=(None,None)  # Closest centre to user's latest click.
        self.distance=0               # Length of generated line
        self.visited=[]

        # Setting the dictionary of centres and contours. The constructor  of this class calls the calculateContours function that performs hole detection using Computer Vision.
        self.calculateContours(img)   
    
    # Function to create the mapping between all hole centres(Key) and their respective contours(Items).
    def calculateContours(self,img):

        # Calculating contours
        new_image = img.copy()
        thresh= cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(thresh, CANNY_MIN_THRESHOLD, CANNY_MAX_THRESHOLD)  # Canny edge detection
        cnts = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Drawing the contours
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        
        # Looping through contours to to find best 
        for i in cnts:
            M = cv2.moments(i)
            if M['m00'] != 0:

                # Performing a check to make sure other contours in the image are not detected.
                if(cv2.contourArea(i) < MAX_AREA):
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    self.cnt_dict[(cx,cy)]=i

        if(len(self.cnt_dict)==0):
            print(" No contours detected! ")

    # Calculation of Euclidean distance between two selected centres of points. 
    def calculateDistance(self):
        self.distance=math.sqrt(pow(self.x1-self.x2,2) + pow(self.y1-self.y2,2))
    
    # This function calculates the closest hole to the user's mouse click.
    def calculateClosest(self,x,y):

        # Initializing minimum distance and closest point.
        closest=THRESHOLD_DISTANCE
        val=(None,None)

        # Looping through all keys in the dictionary of contours.
        for i in list(self.cnt_dict.keys()):

            # Euclidean distance
            dist=math.sqrt(pow(x-i[0],2) + pow(y-i[1],2))

            # Check for points closer than the threshold limit.
            if(dist<closest):
                closest=dist
                val=i
        # If a point is close enough to a hole.
        if val!=(None,None):

            # Appending all points to the list as required
            self.visited.append(val)

            # Setting the value of the 1st point.
            if(self.x1==None):
                self.x1=val[0]
                self.y1=val[1]

            # Setting the value of the 2nd point.
            else:
                self.x2=val[0]
                self.y2=val[1]

            # Updating the latest closest point.
            self.closest=val

        else:
            print(" Point is too far away! ")
    
    #####################################################
    """ Get functions for all the critical values """

    # Returns distance of 2 points and returns the euclidean distance.
    def getDistance(self):
        self.calculateDistance()
        return self.distance

    # Returns closest coordinate of currently selcted hole.
    def getClosest(self,x,y):
        self.calculateClosest(x,y)
        return self.closest

    ######################################################
    
        

if __name__=="__main__":

    # Obtaining arguments from start scripts.
    parser=OptionParser()

    # Path to image
    parser.add_option("-p","--path",dest="img_location",default=DEFAULT_IMAGE_PATH)

    # Scale factor
    parser.add_option("-s","--scale",dest="scale_factor",type=float,default=DEFAULT_SCALING_FACTOR)

    # Draw colors.
    parser.add_option("-c","--color",dest="pen_color",nargs=3,type=int,default=DEFAULT_COLOR)

    # Understand type.
    parser.add_option("-t","--type",dest="file_type",default=DEFAULT_FILE_TYPE)

    (options, args) = parser.parse_args()

    root=Tk()

    
    main_frame=ViewerFrame(root,options=options)

    main_frame.mainloop()



