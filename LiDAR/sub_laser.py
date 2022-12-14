import rclpy, sys
from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from ar_track.move_tb3 import MoveTB3
from math import radians, degrees, sqrt, atan2

from std_msgs.msg import String

class SubLaser(Node):
    
    def __init__(self):
        super().__init__('sub_laser')
        #qos_profile = QoSProfile(depth=10)
        
        # define subscriber
        self.sub_scan = self.create_subscription(
           LaserScan,           # topic type
            '/scan',        # topic name
            self.get_scan,   # callback function
            qos_profile_sensor_data)
        self.scan = LaserScan()
        self.move_tb3 = MoveTB3()
        
        self.laser_cam_pub = self.create_publisher(String, 'laser_cam', 10)
        
        self.point_control = self.create_publisher(String, 'waypoint_control', 10)
        
    def get_scan(self, msg):
        self.scan = msg
        print("front = %s" %(self.scan.ranges[0]))
        print("left  = %s" %(self.scan.ranges[90]))
        print("back  = %s" %(self.scan.ranges[180]))
        print("right = %s" %(self.scan.ranges[270]))
        print("--------------------------")
        
        for i in range(0, 360):
        	#angle_sum = 0
        	#stack = 1
        	#angle_avg = 0
        	if (0.0 < float(self.scan.ranges[i]) < 0.4):
        		topic = String()
        		topic.data = 'stop'
        		self.point_control.publish(topic)
        		
        		msg = String()
        		msg.data = 'find'
        		self.laser_cam_pub.publish(msg)
        		
        		print(i, "도 방향 !!!!!!!")
        		if (i > 180):
        			self.move_tb3.rotate(radians(-(360-i-10)))
        			self.move_tb3.straight(-0.08)
        			msg.data = 'end_find'
        			self.laser_cam_pub.publish(msg)
        			
        			topic.data = 'go'
        			self.point_control.publish(topic)
        			
        			break
        		else:
        			self.move_tb3.rotate(radians(i+20))
        		    self.move_tb3.straight(-0.08)
        			msg.data = 'end_find'
        			self.laser_cam_pub.publish(msg)
        			
        			topic.data = 'go'
        			self.point_control.publish(topic)
        			
        			break
            	
            	#msg = String()
            	
        
        
def main(args=None):
    rclpy.init(args=args)
    node = SubLaser()
    
    try:
        rclpy.spin(node)
                
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard Interrupt(SIGINT)')
        
    finally:
        node.destroy_node()
        rclpy.shutdown()
    
            
if __name__ == '__main__':
    main()
