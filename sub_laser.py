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
        
        #self.laser_cam_pub = self.create_publisher(String, 'laser_cam', 10)
        
        
    def get_scan(self, msg):
        self.scan = msg
        #print("front = %s" %(self.scan.ranges[0]))
        #print("left  = %s" %(self.scan.ranges[90]))
        #print("back  = %s" %(self.scan.ranges[180]))
        #print("right = %s" %(self.scan.ranges[270]))
        #print("--------------------------")
        
        
        #a = radians(float(input("input rotation (deg): ")))
        #d = float(input("input distance (m)  : "))
        #node.rotate(a)
        #node.straight(d)
        
        #self.move_tb3.straight(0.5)
        #self.enermy = 1
        #self.angle_stack = 0
        for i in range(0, 360):
        #    print("angle[%d] : %s" %(i, self.scan.ranges[i]))
            if (float(self.scan.ranges[i]) > 0.0 and float(self.scan.ranges[i]) < 0.2):
        #        msg = String()
        #        msg.data = 'find'
        #        self.laser_cam_pub.publish(msg)
                
                self.move_tb3.rotate(radians(i))
        #        self.move_tb3.straight(-0.2)
        #    	self.angle_stack += i
        #    	self.enermy += 1

        #if 30 < self.enermy <= 50:
        #	print(self.angle_stack // self.enermy, "도 방향 미상물체 접근중!!!!!!!")
        #	self.move_tb3.rotate(radians(self.angle_stack // self.enermy))
        
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
