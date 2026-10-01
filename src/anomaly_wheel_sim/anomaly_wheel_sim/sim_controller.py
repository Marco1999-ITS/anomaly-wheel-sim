import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64
from sensor_msgs.msg import JointState
from visualization_msgs.msg import Marker
from builtin_interfaces.msg import Duration
import math
import json

class SimController(Node):
    def __init__(self):
        super().__init__('sim_controller')

        self.current_angle = 0.0
        self.target_speed = 3.0 
        self.latest_status = "unknown"
        self.prev_status = None 
        self.last_telemetry_time = self.get_clock().now()

        self.create_subscription(String, 'nicla_telemetry', self.telemetry_cb, 10)
        self.create_subscription(Float64, '/target_speed', self.speed_cb, 10)

        self.pub_joint = self.create_publisher(JointState, '/joint_states', 10)
        self.pub_marker = self.create_publisher(Marker, '/anomaly_marker', 10)

        self.timer_period = 0.033
        self.timer = self.create_timer(self.timer_period, self.control_loop)
        
        self.watchdog = self.create_timer(0.5, self.watchdog_check)
        
        self.get_logger().info("Supervisore avviato. Log latenze attivo.")

    def speed_cb(self, msg):
        self.target_speed = msg.data

    def watchdog_check(self):
        time_since_last = (self.get_clock().now() - self.last_telemetry_time).nanoseconds / 1e9
        if time_since_last > 1.0:
            self.latest_status = "timeout"

    def telemetry_cb(self, msg):
        self.last_telemetry_time = self.get_clock().now()
        try:
            data = json.loads(msg.data)
            
            if 'status' in data:
                self.latest_status = data['status'].strip()
            
            pc_rx_time = data.get('pc_rx_time', 0.0)
            nicla_dsp_ms = data.get('dsp_ms', 0)
            nicla_class_ms = data.get('class_ms', 0)

            if pc_rx_time > 0 and self.latest_status not in ["norma", "unknown"]:
                current_time = self.get_clock().now().nanoseconds / 1e9
                ros_latency_ms = (current_time - pc_rx_time) * 1000.0
                
                self.get_logger().warn(
                    f"[{self.latest_status.upper()}] "
                    f"MCU: {nicla_dsp_ms + nicla_class_ms} ms | "
                    f"ROS Latenza: {ros_latency_ms:.2f} ms"
                )
                
        except json.JSONDecodeError:
            pass

    def control_loop(self):
        now = self.get_clock().now().to_msg()
        
        speed_multiplier = 0.0
        alert_text = ""
        cube_color = (0.0, 0.0, 0.0)
        
        if self.latest_status in ["anomalia 2", "anomalia2"]:
            speed_multiplier = 0.1 
            alert_text = "ALLARME CRITICO"
            cube_color = (1.0, 0.0, 0.0) 
        elif self.latest_status == "anomalia1":
            speed_multiplier = 0.5 
            alert_text = "MICRO-VIBRAZIONI"
            cube_color = (1.0, 0.5, 0.0) 
        elif self.latest_status == "norma":
            speed_multiplier = 1.0 
        elif self.latest_status == "timeout":
            speed_multiplier = 0.0 
            alert_text = "SCONNESSO"
            cube_color = (0.5, 0.5, 0.5)
        else:
            speed_multiplier = 0.0
            alert_text = "STATO IGNOTO"
            cube_color = (1.0, 0.0, 1.0) 
            
        actual_speed = self.target_speed * speed_multiplier
        self.current_angle += actual_speed * self.timer_period
        
        js = JointState()
        js.header.stamp = now
        js.name = ['wheel_joint'] 
        js.position = [self.current_angle % (2 * math.pi)]
        self.pub_joint.publish(js)
        
        if self.latest_status != self.prev_status:
            m_text = Marker()
            m_text.header.frame_id = "nicla_link" 
            m_text.header.stamp = now
            m_text.ns = "text_anomalies"
            m_text.id = 0
            m_text.type = Marker.TEXT_VIEW_FACING
            m_text.lifetime = Duration(sec=0, nanosec=0) 
            
            m_cube = Marker()
            m_cube.header.frame_id = "nicla_link" 
            m_cube.header.stamp = now
            m_cube.ns = "sensor_highlights"
            m_cube.id = 1
            m_cube.type = Marker.CUBE
            m_cube.lifetime = Duration(sec=0, nanosec=0) 

            if alert_text == "":
                m_text.action = Marker.DELETE
                m_cube.action = Marker.DELETE
            else:
                m_text.action = Marker.ADD
                m_cube.action = Marker.ADD
                
                m_text.pose.position.z = 0.3
                m_text.scale.z = 0.15
                m_text.color.a = 1.0
                m_text.color.r = 1.0; m_text.color.g = 1.0; m_text.color.b = 0.0
                m_text.text = alert_text
                
                m_cube.scale.x = 0.08; m_cube.scale.y = 0.08; m_cube.scale.z = 0.04
                m_cube.color.a = 0.7
                m_cube.color.r, m_cube.color.g, m_cube.color.b = cube_color

            self.pub_marker.publish(m_text)
            self.pub_marker.publish(m_cube)
            
            self.prev_status = self.latest_status

def main(args=None):
    rclpy.init(args=args)
    try:
        node = SimController()
        rclpy.spin(node)
    except Exception:
        pass
    finally:
        if rclpy.ok(): 
            rclpy.shutdown()

if __name__ == '__main__':
    main()