
import cv2
import numpy as np
import argparse as arg
from numpy.typing import NDArray

points = []
state = False #Variable to define if we want to finish making points and estimate the perimeter.
afk = 1

def user_interaction()-> arg.ArgumentParser:
    parser = arg.ArgumentParser(description='dimension measurment')
    parser.add_argument("-c",'--cam_index', 
                        type=int, 
                        default=0, 
                        help='Camera index for the measurment')
    parser.add_argument('--z', 
                        type=int, 
                        help='Depth within the camera and the object')
    parser.add_argument('--cal_file', 
                        type=str, 
                        help='Path to the calibration JSON object')
    args = parser.parse_args()
    return args

def initialise_camera(args:arg.ArgumentParser)->cv2.VideoCapture:
    cap = cv2.VideoCapture(args.cam_index)
    return cap 

# Define a callback function to capture mouse events
def mouse_interaction(event,x,y,flags,params):
    global state
    global afk
    if event == cv2.EVENT_LBUTTONDOWN and state == False:
        points.append((x,y))
    if flags & cv2.EVENT_FLAG_CTRLKEY:
        points.clear()
        state = False
    if event == cv2.EVENT_MBUTTONDOWN and len(points)!= 0:
        state = True
        afk = 0
        if len(points)>2:
            points.append(points[0])

#Function to draw lines in the frame   
def draw_lines(frame:NDArray)->None:
    cnt = 0
    #We name the window we want the drawings to be shown in
    cv2.namedWindow('image')

    #Track the mouse events
    cv2.setMouseCallback("image",mouse_interaction)

    #Loop to draw evey single dot and link these.
    for point in points:
        cv2.circle(frame,(point[0],point[1]),3,(0,0,0),-1)
        cnt +=1
        if cnt > 1:
            previous = points[cnt-2] 
            cv2.line(frame,point,previous,(0,0,0),1)

    #The frame is shown
    cv2.imshow("image",frame) 
    return None

#Function to compute the line lenghts 
def compute_line_segments()->tuple[list[tuple[str, float]],list[tuple[str, float]]]:
    cnt = 0
    global state
    lengths = []
    consecutive_points = []
    if len(points) >= 2 and state == True:
        for point in points:
            cnt +=1
            if cnt > 1:
                previous = points[cnt-2]
                x = (point[0]-previous[0])**2
                y = (point[1]-previous[1])**2
                lengths.append(("P{}{}:".format(cnt-2,cnt-1),np.sqrt(x+y)))
                consecutive_points.append(("P{}{}:".format(cnt-2,cnt-1),np.sqrt(x+y)))
    #We sort the array from bigger to smaller.
    
    lengths.sort(key=lambda x: x[1], reverse=True)
    return lengths, consecutive_points

#function to compute the perimeter of the figure
def compute_perimeter(lengths:NDArray)->float:
    perimeter = 0
    #We just compute it if there are more than two lines.
    if len(lengths)>2:
        for point in lengths:
            perimeter += point[1]
    return perimeter

def print_results(lengths:list,perimeter:float,consecutive:list)->None:
    global afk
    print("------------------------------------")
    print("Distance between consecutive points")
    for length in consecutive:
        print(length[0],length[1])
    print("List in ascending order")
    for length in lengths:
        print(length[0],length[1])
    if perimeter!=0:
        print("Perimeter:",perimeter)
    if len(points) < 2 and state == True:
        P = points[0]
        print("Just one point was selected with coordinates",P[0],P[1])
    print("------------------------------------")
    afk = 1
    return None

def pipeline():
    global afk
    args = user_interaction()
    cap = initialise_camera(args)
    while cap.isOpened():
        # Read current frame
        ret, frame = cap.read()

        # Check if the image was correctly captured
        if not ret:
            print("ERROR! - current frame could not be read")
            break
        #Draw the mouse callback
        draw_lines(frame)
        #Estimate and sort the line lengths 
        lengths,consecutive_points = compute_line_segments()
        #Estimate the perimeter in case the figure has more than 2 lines
        perimeter = compute_perimeter(lengths)

        if afk == 0:
            print_results(lengths,perimeter,consecutive_points)

        key = cv2.waitKey(10)
        if key == ord('q') or key == 27:
            print("Programm finished!")
            break
    cv2.destroyAllWindows()
    cap.release()
    return None

if __name__ == "__main__":
    pipeline()
