import os 
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable  # <-- Agregamos SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro
from launch.actions import TimerAction

def generate_launch_description():
    
    robotName = 'my_robot'
    namePackage = 'mobile_robot'
  
    mobileFileRelativePath = 'model/robot.xacro'
    
    pathModelFile = os.path.join(get_package_share_directory(namePackage), mobileFileRelativePath)
    
    # Procesamos el xacro y lo convertimos a string XML
    robotDescriptionXML = xacro.process_file(pathModelFile).toxml()
    
    # --- AQUÍ ESTÁ EL TRUCO PARA DETENER EL SEGMENTATION FAULT ---
    # Obligamos a Ogre2 a compartir el contexto gráfico entre la GUI y el hilo del Lidar
    force_share_context = SetEnvironmentVariable(name='OGRE2_SHARE_CONTEXT', value='1')
    
    # Gazebo Sim
    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
    )
    
    # Ruta al archivo del laberinto corregido
    path_world = os.path.join(get_package_share_directory(namePackage), 'world', 'laberinto_prueba.sdf')
    
    # Argumentos para cargar el mapa mundial modificado
    gazeboLaunch = IncludeLaunchDescription(
        gazebo_rosPackageLaunch, 
        launch_arguments={'gz_args': f'-r -v 4 {path_world}'}.items() 
    )
    
    # Node 1: Robot State Publisher
    nodeRobotStatePublisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robotDescriptionXML, 
            'use_sim_time': True
        }]
    )
    
    # Node 2: Spawn Model (Con retraso de 5 segundos para estabilidad)
    spawnModelNodeGazebo = TimerAction(
        period=5.0,
        actions=[Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-name', robotName, '-topic', 'robot_description'],
            output='screen',
        )]
    )
    
    return LaunchDescription([
        force_share_context,  # <-- Se ejecuta en primer lugar para preparar la GPU
        gazeboLaunch,
        nodeRobotStatePublisher,
        spawnModelNodeGazebo,
    ])