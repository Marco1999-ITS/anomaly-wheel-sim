from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'anomaly_wheel_sim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
       
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
       
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rosuser',
    maintainer_email='marcoantoniolorusso@yahoo.it',
    description='Simulazione ruota con rilevamento anomalie',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'serial_bridge = anomaly_wheel_sim.serial_bridge:main',
            'sim_controller = anomaly_wheel_sim.sim_controller:main',
        ],
    },
)