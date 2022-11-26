import rclpy, sys
from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from ar_track.move_tb3 import MoveTB3
from math import radians, degrees, sqrt, atan2
from geometry_msgs.msg import Twist
from rcl_interfaces.srv import SetParameters, GetParameters, ListParameters
from rclpy.exceptions import ParameterNotDeclaredException
from rclpy.parameter import Parameter

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
        self.scan	= LaserScan()
        self.tb3 	= MoveTB3()
        self.laser_cam_pub = self.create_publisher(String, 'laser_cam', 10)
        
        self.tw 	= Twist()
        self.cli = self.create_client(GetParameters, 'client_follow_points/get_parameters')
        self.cli = self.create_client(SetParameters, 'client_follow_points/set_parameters')
        self.req = SetParameters.Request()
        self.count = 1
    
    def send_request(self):
    	param = self.cli.get_parameter('waypoints').get_parameter_value().string_value
    	self.count = param + 1
    	self.req.parameters = [Parameter(name='waypoints', value=self.count).to_parameter_msg()]
    	self.future = self.cli.call_async(self.req)
    
        
    def get_scan(self, msg):
        self.scan = msg
        print("front = %s" %(self.scan.ranges[0]))
        print("left  = %s" %(self.scan.ranges[90]))
        print("back  = %s" %(self.scan.ranges[180]))
        print("right = %s" %(self.scan.ranges[270]))
        print("--------------------------")
        
        #client = ReqSetParam()

        for i in range(0, 360):
        	if 0.0 < float(self.scan.ranges[i]) < 0.35:
        		msg = String()
        		msg.data = 'find'
        		self.laser_cam_pub.publish(msg)
        		
        		print(i, "도 방향 발견")
        		if i>180:
        			r = -(360 - i-10)
        			self.tb3.rotate(radians(r))
        			self.tb3.straight(-0.1)
        			msg.data = 'end_find'
        			self.laser_cam_pub.publish(msg)
        			self.send_request()
        			break
        		else:
        			self.tb3.rotate(radians(i+20))
        			self.tb3.straight(-0.1)
        			msg.data = 'end_find'
        			self.laser_cam_pub.publish(msg)
        			self.send_request()
        			break
        
        
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
