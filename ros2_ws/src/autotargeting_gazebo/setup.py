import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'autotargeting_gazebo'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.*'))),
        (os.path.join('share', package_name, 'urdf'), glob(os.path.join('urdf', '*.*'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='AutoTargeting',
    maintainer_email='autotargeting@example.com',
    description='Gazebo Fortress pan-tilt simulation for AutoTargeting.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pan_tilt_bridge_node = autotargeting_gazebo.pan_tilt_bridge_node:main',
        ],
    },
)
