from setuptools import find_packages, setup

import os 
from glob import glob


package_name = 'mobile_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'world'), glob('world/*.sdf')),
        (os.path.join('share', package_name, 'parameters'), glob('parameters/*')),
        # Copia los archivos base del modelo (model.config y model.sdf)
        (os.path.join('share', package_name, 'model/maze_model_rs'), glob('model/maze_model_rs/*.config')),
        (os.path.join('share', package_name, 'model/maze_model_rs'), glob('model/maze_model_rs/*.sdf')),
        # Copia las subcarpetas necesarias
        (os.path.join('share', package_name, 'model/maze_model_rs/media'), glob('model/maze_model_rs/media/*')),
        (os.path.join('share', package_name, 'model/maze_model_rs/thumbnails'), glob('model/maze_model_rs/thumbnails/*')),
        (os.path.join('share', package_name, 'model'), glob('model/robot.xacro')),
        (os.path.join('share', package_name, 'model'), glob('model/robot.gazebo')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rueda',
    maintainer_email='rueda@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'lidar_min = mobile_robot.lidar_min:main',
        ],
    },
)
