import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class LidarRightHandRule(Node):
    def __init__(self):
        super().__init__('lidar_right_hand_rule')
        
        # 1. Suscriptor para el LiDAR
        self.create_subscription(
            LaserScan,
            '/scan',
            self.listener_callback,
            10
        )
        
        # 2. Publicador de velocidad hacia los motores
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 3. Parámetros físicos de control (Mano Derecha)
        self.distancia_deseada = 0.6  # Distancia ideal a mantener de la pared derecha (metros)
        self.umbral_frontal = 0.8     # Distancia crítica para esquivar obstáculos frontales

    def listener_callback(self, msg):
        # Filtro de seguridad: Reemplaza infinitos o lecturas erróneas por 10 metros
        ranges = [r if (msg.range_min < r < msg.range_max) else 10.0 for r in msg.ranges]
        n = len(ranges) # Ahora este valor será 360

        # Si por alguna razón el sensor no se ha reiniciado en la simulación, evitamos errores
        if n < 360:
            return

        # SECTORES EXACTOS PARA 360 PUNTOS
        # Frente (Ángulo 0° -> Índice 180). Tomamos un cono de visión de +/- 20 puntos
        frente = min(min(ranges[160:200]), 10.0)
        
        # Derecha (Ángulo -90° -> Índice 90). Tomamos un cono de visión de +/- 20 puntos
        derecha = min(min(ranges[70:110]), 10.0)

        # Monitoreo en consola
        self.get_logger().info(f"SCAN 360 -> Frente: {frente:.2f}m | Derecha: {derecha:.2f}m")

        msg_vel = Twist()

        # =========================================================================
        # LÓGICA DE CONTROL PROPORCIONAL CORREGIDA (Signos de giro ROS)
        # =========================================================================
        msg_vel = Twist()

        # SECTORES (360 puntos en total)
        frente = min(min(ranges[170:190]), 10.0) 
        derecha = min(min(ranges[70:110]), 10.0)

        self.get_logger().info(f"Frente: {frente:.2f}m | Derecha: {derecha:.2f}m")

        # 1. OBSTÁCULO AL FRENTE (Evitar choque frontal)
        if frente < 0.4:
            msg_vel.linear.x = 0.1    # Avanza un mínimo para no pivotar estático
            msg_vel.angular.z = 1.5   # Gira a la IZQUIERDA (Positivo) para esquivar
            self.get_logger().warn("¡FRENTE BLOQUEADO! Girando a la izquierda.")

        # 2. SEGUIMIENTO DE PARED DERECHA
        else:
            error = derecha - self.distancia_deseada
            
            # Kp asigna la fuerza del volantazo.
            # Multiplicamos por NEGATIVO para que:
            # - Si error > 0 (lejos), angular.z sea NEGATIVO (gira a la DERECHA para acercarse).
            # - Si error < 0 (cerca), angular.z sea POSITIVO (gira a la IZQUIERDA para alejarse).
            Kp = 2.5 
            giro_proporcional = -error * Kp

            # Acotamos el giro máximo para evitar que trompee descontrolado
            msg_vel.angular.z = max(min(giro_proporcional, 1.5), -1.5)

            # Velocidad lineal adaptativa para dar estabilidad
            if abs(error) > 0.3:
                msg_vel.linear.x = 0.6  # Va más lento en curvas o si está muy desalineado
            else:
                msg_vel.linear.x = 0.8  # Velocidad crucero segura en rectas

        # Publicar movimiento
        self.publisher.publish(msg_vel)
def main(args=None):
    rclpy.init(args=args)
    node = LidarRightHandRule()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()