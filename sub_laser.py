import rclpy, sys
from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from ar_track.move_tb3 import MoveTB3
from math import radians, degrees, sqrt, atan2

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
        
        
    def get_scan(self, msg):
        self.scan = msg
        print("front = %s" %(self.scan.ranges[0]))
        print("left  = %s" %(self.scan.ranges[90]))
        print("back  = %s" %(self.scan.ranges[180]))
        print("right = %s" %(self.scan.ranges[270]))
        print("--------------------------")
        #a = radians(float(input("input rotation (deg): ")))
        #d = float(input("input distance (m)  : "))
        #node.rotate(a)
        #node.straight(d)
        
        #self.move_tb3.straight(0.5)
        
        for i in range(0, 360):
            if (float(self.scan.ranges[i]) > 0.2 and float(self.scan.ranges[i]) < 0.3):
            	print(i, "도 방향 미상물체 접근중!!!!!!!")
            	self.move_tb3.rotate(radians(i))
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

