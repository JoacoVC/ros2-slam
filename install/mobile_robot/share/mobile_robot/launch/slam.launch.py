import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_path = get_package_share_directory('mobile_robot')

    # --- 1. Definición de rutas 
    rviz_config_dir = os.path.join(pkg_path, 'rviz', 'mi_configuracion.rviz')

    # 2. Lanzamiento de Gazebo
    gazebo_model = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_path, 'launch', 'gazebo_model.launch.py')
        )
    )

    # 3. Nodo del Bridge
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(pkg_path, 'parameters', 'bridge_parameters.yaml'),
            'use_sim_time': True
        }],
        output='screen'
    )

    # 4. SLAM Toolbox
    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'slam_params_file': os.path.join(pkg_path, 'parameters', 'slam_params.yaml'),
            'use_sim_time': 'true'
        }.items()
    )
    
    # 5. Lifecycle Manager
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_slam',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['slam_toolbox']
        }]
    )

    # 6. RViz2 
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_dir],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    lidar_right_hand = Node(
    package='mobile_robot',
    executable='lidar_min',
    name='lidar_right_hand_rule',
    output='screen',
    )

    return LaunchDescription([
        gazebo_model,
        gz_bridge,
        slam_toolbox,
        lifecycle_manager,
        rviz_node,
        lidar_right_hand
    ])