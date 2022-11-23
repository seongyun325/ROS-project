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
        
        self.red_pub_return = self.create_publisher(String, 'color_red_return', 10)

    def shooting_callback(self, data):
        ser.write(1)
        while (1):
            if ser.readable():	# 아두이노에서 값이 반환되었을 때
                arduino_response = ser.readline()
                
                #print(arduino_response[:len(arduino_response)-1].decode())
                
                msg = String()
                msg.data = arduino_response[:len(arduino_response)-1].decode()
                self.red_pub_return.publish(msg)
                break

def main(args=None):
    
    rclpy.init(args=args)
    node = Red_shooting()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
