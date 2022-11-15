import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
import time

ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
ser.flush()

class Red_shooting(Node):

    def __init__(self):
        super().__init__('redShooting')

        self.subscription = self.create_subscription(String, 
                'color_red', 
                self.shooting_callback, 
                10)

    def shooting_callback(self, data):
        ser.write(1)
        #time.sleep(5)

def main(args=None):
    
    rclpy.init(args=args)
    node = Red_shooting()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
