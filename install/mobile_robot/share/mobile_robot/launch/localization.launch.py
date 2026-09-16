import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_path = get_package_share_directory('mobile_robot')
    map_file = os.path.join(pkg_path, 'maps', 'mi_mapa.yaml')
    amcl_config = os.path.join(pkg_path, 'parameters', 'amcl_params.yaml')

    return LaunchDescription([
        # 1. Servidor de Mapas
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[{'yaml_filename': map_file, 'use_sim_time': True}]
        ),

        # 2. AMCL (Localización)
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            parameters=[amcl_config]
        ),

        # 3. Lifecycle Manager 
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            parameters=[{'autostart': True, 'node_names': ['map_server', 'amcl']}]
        )
    ])