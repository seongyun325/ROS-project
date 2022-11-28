import rclpy, time
from rclpy.node import Node
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseStamped 
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from nav2_msgs.action import FollowWaypoints
# from rclpy.duration import Duration # Handles time for ROS 2
from rclpy.exceptions import ParameterNotDeclaredException
from rcl_interfaces.msg import ParameterType

from std_msgs.msg import String

go_stop = 'go'

class ClientFollowPoints(Node):

    def __init__(self):
        super().__init__('client_follow_points')
        self._client = ActionClient(self, FollowWaypoints, '/FollowWaypoints')
        #self.declare_parameter('mode', 'move')
        self.go_stop_sub = self.create_subscription (
        	String,
        	'waypoint_control',
        	self.go_stop_callback,
        	10)

        self.declare_parameter('waypoints', 'point1')
        timer_period = 1	# seconds
        self.timer = self.create_timer(timer_period, self.send_waypoints)
        self.tw = Twist()
        self.rgoal = PoseStamped()
        
    
    def go_stop_callback(self, data):
    	global go_stop
    	go_stop = data.data
        
    def send_waypoints(self):
    	global go_stop
    	param = self.get_parameter('waypoints').get_parameter_value().string_value
    	
    	if go_stop == 'go':
    		if param == 'point1':
    			#print("11111111")
    			self.rgoal.header.frame_id = "map"
    			self.rgoal.header.stamp.sec = 0
    			self.rgoal.header.stamp.nanosec = 0
    			
    			self.rgoal.pose.position.z = -0.00143
    			self.rgoal.pose.position.x = 0.661
    			self.rgoal.pose.position.y = 0.157
    			
    			self.rgoal.pose.orientation.w = 1.0
    		elif param == 'point2':
    			#print("22222222")
    			self.rgoal.header.frame_id = "map"
    			self.rgoal.header.stamp.sec = 0
    			self.rgoal.header.stamp.nanosec = 0
    			
    			self.rgoal.pose.position.z = -0.00143
    			self.rgoal.pose.position.x = 1.03
    			self.rgoal.pose.position.y = -0.345
    			
    			self.rgoal.pose.orientation.w = 1.0
    		elif param == 'point3':
    			#print("33333333")
    			self.rgoal.header.frame_id = "map"
    			self.rgoal.header.stamp.sec = 0
    			self.rgoal.header.stamp.nanosec = 0
    			
    			self.rgoal.pose.position.z = -0.00143
    			self.rgoal.pose.position.x = 1.91
    			self.rgoal.pose.position.y = -0.195
    			
    			self.rgoal.pose.orientation.w = 1.0
    			
    		self.get_logger().info('%s' % param)
    		mgoal = [self.rgoal]
    		self.send_points(mgoal)
    	else:
    		self.tw.linear.x = 0.0
    		self.tw.angular.z = 0.0
    		
    def send_points(self, points):
        msg = FollowWaypoints.Goal()
        msg.poses = points

        self._client.wait_for_server()
        self._send_goal_future = self._client.send_goal_async(msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info('Result: {0}'.format(result.missed_waypoints))

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info('Received feedback: {0}'.format(feedback.current_waypoint))

def main(args=None):
    rclpy.init(args=args)

    follow_points_client = ClientFollowPoints()
    
    rclpy.spin(follow_points_client)
	
    	
if __name__ == '__main__':
	main()
