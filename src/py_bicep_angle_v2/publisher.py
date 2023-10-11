# Basic ROS 2 program to publish real-time streaming 
# video from your built-in webcam
# Author:
# - Addison Sears-Collins
# - https://automaticaddison.com
   
# Import the necessary libraries
import rclpy # Python Client Library for ROS 2
from rclpy.node import Node # Handles the creation of nodes
from sensor_msgs.msg import Image # Image is the message type
from cv_bridge import CvBridge # Package to convert between ROS and OpenCV Images
import cv2 # OpenCV library
import mediapipe as mp
import time
import math
from std_msgs.msg import String
from std_msgs.msg import Int32


def calculate_bicep_angle(side_shoulder, side_elbow, side_wrist):
    angle = math.degrees(math.acos((side_shoulder * side_shoulder + side_wrist * side_wrist - side_elbow * side_elbow)/(2.0 * side_shoulder * side_wrist)))
    return angle


class ImagePublisher(Node):
  """
  Create an ImagePublisher class, which is a subclass of the Node class.
  """
  def __init__(self):
    """
    Class constructor to set up the node
    """
    # Initiate the Node class's constructor and give it a name
    super().__init__('image_publisher')
       
    # Create the publisher. This publisher will publish an Image
    # to the video_frames topic. The queue size is 10 messages.
    self.publisher_ = self.create_publisher(Image, 'video_frames', 10)
    self.left_arm_publisher = self.create_publisher(Int32, 'left_arm', 10)
    self.right_arm_publisher = self.create_publisher(Int32, 'right_arm', 10)


    # We will publish a message every 0.1 seconds
    timer_period = 0.1  # seconds
       
    # Create the timer
    self.mp_drawing = mp.solutions.drawing_utils
    self.mp_holistic = mp.solutions.holistic

    self.holistic = self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    self.timer = self.create_timer(timer_period, self.timer_callback)
          
    # Create a VideoCapture object
    # The argument '0' gets the default webcam.
    self.cap = cv2.VideoCapture(0)
    self.cap.set(3,1280)
    self.cap.set(4,720)

    # Used to convert between ROS and OpenCV images
    self.br = CvBridge()
    
  def timer_callback(self):
    """
    Callback function.
    This function gets called every 0.1 seconds.
    """
    # Capture frame-by-frame
    # This method returns True/False as well
    # as the video frame.
    

    ret, frame = self.cap.read()
    left_bicep_angle = 0
    right_bicep_angle = 0

    if ret == True:
      # Publish the image.
      # The 'cv2_to_imgmsg' method converts an OpenCV
      # image to a ROS 2 image message

      results = self.holistic.process(frame)
      self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_holistic.POSE_CONNECTIONS)

      # [Shoulder, Elbow, Wrist]
      left_hand_points = [0,0,0]
      right_hand_points = [0, 0, 0]

      # [Top Left, Top Right, Bot Left, Bot Right]
      body_points = [0,0,0,0]




      if results.pose_landmarks:
          for index, landmark in enumerate(results.pose_landmarks.landmark):
              height, width, c = frame.shape
              x_coord = int(landmark.x * width)
              y_coord = int(landmark.y * height)

              displayed_points = [12,14,16,11,13,15,23,24]
              if index in displayed_points:

                  cv2.putText(frame, str(str(x_coord) + ", " + str(y_coord)), (x_coord, y_coord),
                              cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                  cv2.circle(frame, (x_coord, y_coord), 10, (255,0,255), cv2.FILLED)

                  # Goes through all the possible points for each arm and puts them into correct list & position
                  if index == 11:
                      left_hand_points[0] = landmark
                      body_points[1] = landmark
                  elif index == 12:
                      right_hand_points[0] = landmark
                      body_points[0] = landmark
                  elif index == 13:
                      left_hand_points[1] = landmark
                  elif index == 14:
                      right_hand_points[1] = landmark
                  elif index == 15:
                      left_hand_points[2] = landmark
                  elif index == 16:
                      right_hand_points[2] = landmark
                  elif index == 23:
                      body_points[2] = landmark
                  elif index == 24:
                      body_points[3] = landmark

          # Left Bicep Calculations
          point_left_shoulder = [left_hand_points[0].x * width, left_hand_points[0].y * height]
          point_left_elbow = [left_hand_points[1].x * width, left_hand_points[1].y * height]
          point_left_wrist = [left_hand_points[2].x * width, left_hand_points[2].y * height]

          side_left_shoulder = math.dist(point_left_elbow, point_left_wrist)
          side_left_elbow = math.dist(point_left_shoulder, point_left_wrist)
          side_left_wrist = math.dist(point_left_shoulder, point_left_elbow)

          left_bicep_angle = calculate_bicep_angle(side_left_shoulder, side_left_elbow, side_left_wrist)

          # Right Bicep Calculations
          point_right_shoulder = [right_hand_points[0].x * width, right_hand_points[0].y * height]
          point_right_elbow = [right_hand_points[1].x * width, right_hand_points[1].y * height]
          point_right_wrist = [right_hand_points[2].x * width, right_hand_points[2].y * height]

          side_right_shoulder = math.dist(point_right_elbow, point_right_wrist)
          side_right_elbow = math.dist(point_right_shoulder, point_right_wrist)
          side_right_wrist = math.dist(point_right_shoulder, point_right_elbow)

          right_bicep_angle = calculate_bicep_angle(side_right_shoulder, side_right_elbow, side_right_wrist)

          # Display both bicep angles
          cv2.putText(frame, "Left Bicep Angle: " + str(round(left_bicep_angle, 2)) + " deg", (width - 400, 25),
                      cv2.FONT_HERSHEY_PLAIN, 1.5, (252,3,57), 2)
          cv2.putText(frame, "Right Bicep Angle: " + str(round(right_bicep_angle, 2)) + " deg", (width - 400, 60),
                      cv2.FONT_HERSHEY_PLAIN, 1.5, (252, 3, 57), 2)

    
      self.publisher_.publish(self.br.cv2_to_imgmsg(frame))
        
      # Publish left & right bicep angles
      msg_left = Int32()
      msg_right = Int32()

      msg_left.data = int(left_bicep_angle)
      msg_right.data = int(right_bicep_angle)

      self.left_arm_publisher.publish(msg_left)
      self.right_arm_publisher.publish(msg_right)
      
      

  
    # Display the message on the console
    self.get_logger().info('Left Bicep Angle: ' + str(left_bicep_angle) + "\nRight Bicep Angle: " + str(right_bicep_angle))
   
def main(args=None):
   
  # Initialize the rclpy library
  rclpy.init(args=args)
   
  # Create the node
  image_publisher = ImagePublisher()
   
  # Spin the node so the callback function is called.
  rclpy.spin(image_publisher)
   
  # Destroy the node explicitly
  # (optional - otherwise it will be done automatically
  # when the garbage collector destroys the node object)
  image_publisher.destroy_node()
   
  # Shutdown the ROS client library for Python
  rclpy.shutdown()
   
if __name__ == '__main__':
  main()