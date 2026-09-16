import os 
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro
from launch.actions import TimerAction

def generate_launch_description():
    
    robotName = 'my_robot'
    namePackage = 'mobile_robot'
  
    mobileFileRelativePath = 'model/robot.xacro'
    
    pathModelFile = os.path.join(get_package_share_directory(namePackage), mobileFileRelativePath)
    
    #Procesamos el xacro y lo convertimos a string XML
    robotDescriptionXML = xacro.process_file(pathModelFile).toxml()
    
    # Gazebo Sim
    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
    )
    
    path_world = os.path.join(get_package_share_directory(namePackage), 'world', 'laberinto_prueba.sdf')
    
    # Argumentos para cargar el mapa mundial modificado
    gazeboLaunch = IncludeLaunchDescription(
        gazebo_rosPackageLaunch, 
        launch_arguments={'gz_args': f'-r -v 4 {path_world}'}.items() 
    )
    
    # Node 1: Robot State Publisher (PASANDO EL XML REAL)
    nodeRobotStatePublisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robotDescriptionXML, 
            'use_sim_time': True
        }]
    )
    
    spawnModelNodeGazebo = TimerAction(
    period=5.0,
    actions=[Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', robotName, '-topic', 'robot_description'],
        output='screen',
    )]
)
    
    # Node 3: Bridge
    bridge_params = os.path.join(get_package_share_directory(namePackage), 'parameters', 'bridge_parameters.yaml')
    start_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', f'config_file:={bridge_params}'],
        output='screen',
    )
    
    return LaunchDescription([
        gazeboLaunch,
        nodeRobotStatePublisher,
        spawnModelNodeGazebo,
        #start_bridge
    ])