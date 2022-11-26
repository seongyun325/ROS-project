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


class ClientFollowPoints(Node):

    def __init__(self):
        super().__init__('client_follow_points')
        self._client = ActionClient(self, FollowWaypoints, '/FollowWaypoints')
        self.declare_parameter('waypoints', '1')
        timer_period = 5	# seconds
        self.timer = self.create_timer(timer_period, self.send_waypoints)
        self.tw = Twist()
        self.rgoal = PoseStamped()
        
    def send_waypoints(self):
    	param = self.get_parameter('waypoints').get_parameter_value().string_value
    	if param == '0':
    		self.tw.linear.x = 0.0
    		self.tw.angular.z = 0.0
    	elif param == '1':
    		self.rgoal.header.frame_id = "map"
    		self.rgoal.header.stamp.sec = 0
    		self.rgoal.header.stamp.nanosec = 0
    		
    		self.rgoal.pose.position.z = 0.0
    		self.rgoal.pose.position.x = 0.897
    		self.rgoal.pose.position.y = 0.17
    		
    		self.rgoal.pose.orientation.w = 1.0
    	elif param == '2':
    		self.rgoal.pose.position.x = 0.897
    		self.rgoal.pose.position.y = 0.17
    	elif param == '3':
    		self.rgoal.pose.position.x = 0.897
    		self.rgoal.pose.position.y = 0.17	
    		
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
    '''
    rgoal = PoseStamped()
    rgoal.header.frame_id = "map"
    rgoal.header.stamp.sec = 0
    rgoal.header.stamp.nanosec = 0
    
    rgoal.pose.position.z = 0.0
    rgoal.pose.position.x = 0.897
    rgoal.pose.position.y = 0.17
    
    rgoal.pose.orientation.w = 1.0
    '''
    mgoal = [follow_points_client.rgoal]
    follow_points_client.send_points(mgoal)
    rclpy.spin(follow_points_client)
	
    	
if __name__ == '__main__':
	main()
