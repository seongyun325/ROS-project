import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from time import sleep
import numpy as np

from std_msgs.msg import String

from rclpy.qos import QoSProfile
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from rcl_interfaces.srv import SetParameters, GetParameters, ListParameters
from rclpy.exceptions import ParameterNotDeclaredException
from rclpy.parameter import Parameter

find_topic = ''
red_topic = 0

tmp = ' '
 
class ImageSubscriber(Node):

  def __init__(self):
    super().__init__('image_subscriber')
    
    self.sub_scan = self.create_subscription(
           LaserScan,           # topic type
            '/scan',        # topic name
            self.get_scan,   # callback function
            qos_profile_sensor_data)
    self.scan = LaserScan()
    
    self.laser_cam_sub = self.create_subscription(
      String, 
      'laser_cam', 
      self.find_callback, 
      10)
    
    self.clear_sub = self.create_subscription(
      String, 
      'color_red_return', 
      self.clear_callback, 
      10)
    
    self.subscription = self.create_subscription(
      Image, 
      'image_raw', 
      self.listener_callback, 
      10)
    self.subscription
      
    self.br = CvBridge()
    
    self.red_pub = self.create_publisher(String, 'color_red', 10)
    
    self.tw 	= Twist()
    self.cli = self.create_client(SetParameters, 'client_follow_points/set_parameters')
    self.req = SetParameters.Request()
    self.count = 1
    
  def send_request(self):
    if self.count < 3:
    	self.count = self.count + 1
    self.req.parameters = [Parameter(name='waypoints', value='point' + str(self.count)).to_parameter_msg()]
    self.future = self.cli.call_async(self.req)
    
  def get_scan(self, msg):
    #global tmp
    self.scan = msg
    #tmp = self.scan.ranges[0]
    #print("%s" %(self.scan.ranges[0]))
  
  def find_callback(self, msg):
  	global find_topic
  	find_topic = msg.data
  	self.get_logger().info("%s" %(find_topic)) #test
  
  def clear_callback(self, data):
    global red_topic
    
    red_topic = 0
    self.send_request()
  
  def listener_callback(self, data):
    global find_topic
    global red_topic
    
    global tmp
    
    #self.get_logger().info('Receiving video frame')
 
    img_color = self.br.imgmsg_to_cv2(data)
    
    ########################################????????? ?????? ?????? ??? ?????????####################################
    img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)

    hue_red = 0 # ????????? ?????????
    lower_red = (hue_red-10, 100, 100) # ?????????
    upper_red = (hue_red+10, 255, 255) # ?????????
    img_mask = cv2.inRange(img_hsv, lower_red, upper_red) # ????????? ??????

    # kernel = cv2.getStructuringElement( cv2.MORPH_RECT, ( 5, 5 ) )
    # img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_DILATE, kernel, iterations = 3)
    kernel = np.ones((11,11), np.uint8)
    # ?????? ???????????? ?????????(img_mask)?????? ??????????????? 0?????? ????????? ?????????
    # () ?????? ????????? ????????? ?????? ??? ?????? ????????????. (11) ??? ?????? ?????? ??? ????????? ????????? ????????? ??????
    img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_OPEN, kernel)
    # ????????? ?????? ????????? ????????? ??????????????? ??????
    img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_CLOSE, kernel)
    # ?????? ???????????? ??????
    # (Opening ??? Closing ?????? ?????? ?????? ????????? ???????????? ?????????, ???????????? ????????? ????????????.)
    

    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(img_mask)
    # retval : ????????? ?????? ????????? = numOfLabels, img_mask
    # label : ????????? ????????? ??????, ????????? = img_label
    # stats : ??? ????????? ?????? ??????, ?????? ?
    # centroids : ????????? ??????

    max = -1
    max_index = -1 

    for i in range(nlabels):
        if i < 1:
            continue

        area = stats[i, cv2.CC_STAT_AREA]

        if area > max:
            max = area
            max_index = i

    if max_index != -1:
        center_x = int(centroids[max_index, 0])
        center_y = int(centroids[max_index, 1]) 
        left = stats[max_index, cv2.CC_STAT_LEFT]
        top = stats[max_index, cv2.CC_STAT_TOP]
        width = stats[max_index, cv2.CC_STAT_WIDTH]
        height = stats[max_index, cv2.CC_STAT_HEIGHT]

        cv2.rectangle(img_color, (left, top), (left + width, top + height), (0, 0, 255), 5)
        cv2.circle(img_color, (center_x, center_y), 10, (0, 255, 0), -1)
        
        if (find_topic == 'find'):
            #forward_obstacle = 0
            #while(1):
            #    if(0.0 < float(self.scan.ranges[0]) < 0.4):
            #        forward_obstacle = 1
            #        break
            
            if (110 < center_x < 210 and 60 < center_y < 170 and red_topic==0 and 
            		0.0 < float(self.scan.ranges[0]) < 0.5):
                find_topic = 'fing'
                red_topic = 1
                
                self.get_logger().info('center_x : %d, center_y : %d'%(center_x,center_y))
                self.get_logger().info('find red!!!!!!!!!!!!!!!!!!!!!!!!!!!') # ???????????? ????????? ??????
                
                msg = String()
                msg.data = 'red'
                self.red_pub.publish(msg)

    cv2.imshow('RED', img_mask)
    cv2.imshow('Result', img_color)
    ####################################################################################################
    
    # cv2.imshow("camera", img_color)
    
    cv2.waitKey(1)
  
def main(args=None):
  
  rclpy.init(args=args)
  
  image_subscriber = ImageSubscriber()
  
  rclpy.spin(image_subscriber)
  
  image_subscriber.destroy_node()
  
  rclpy.shutdown()
  
if __name__ == '__main__':
  main()
