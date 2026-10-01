import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
import json
import threading
import time 

class NiclaDriver(Node):
    def __init__(self):
        super().__init__('nicla_driver')
        
        self.declare_parameter('port_name', '/dev/ttyACM0')
        port_name = self.get_parameter('port_name').value
        
        self.publisher_ = self.create_publisher(String, 'nicla_telemetry', 10)
        self.running = True 
        
        try:
            self.serial_port = serial.Serial(port_name, 115200, timeout=1.0)
            self.get_logger().info(f"Driver avviato su {port_name}.")
        except Exception as e:
            self.get_logger().error(f"Errore fatale apertura porta {port_name}: {e}")
            raise e

        self.read_thread = threading.Thread(target=self.read_serial_data)
        self.read_thread.start()

    def read_serial_data(self):
        while self.running and rclpy.ok():
            try:
                line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                rx_time_sec = self.get_clock().now().nanoseconds / 1e9 
                
                if line:
                    try:
                        data = json.loads(line)
                        data['pc_rx_time'] = rx_time_sec 
                        
                        msg = String()
                        msg.data = json.dumps(data) 
                        self.publisher_.publish(msg)
                    except json.JSONDecodeError:
                        self.get_logger().warning("JSON scartato.")
                        
            except Exception as e:
                if self.running:
                    self.get_logger().error(f"Errore Seriale: {e}")
                    time.sleep(1.0) 

    def destroy_node(self):
        self.running = False
        if hasattr(self, 'serial_port') and self.serial_port.is_open:
            self.serial_port.close()
        if hasattr(self, 'read_thread'):
            self.read_thread.join()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    try:
        node = NiclaDriver()
        rclpy.spin(node)
    except Exception:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()