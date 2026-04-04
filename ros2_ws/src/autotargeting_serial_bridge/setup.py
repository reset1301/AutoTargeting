# setup.py для пакета типа ament_python: setuptools собирает код,
# colcon вызывает setup.py и регистрирует пакет в overlay workspace.
import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'autotargeting_serial_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    # data_files кладут package.xml и launch в share/, чтобы `ros2 launch` их находил.
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.*'))),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='AutoTargeting',
    maintainer_email='todo@todo',
    description='Serial bridge: pan/tilt angles to Arduino over UART.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Имя команды в PATH после source install/setup.bash — см. `ros2 run ... serial_bridge_node`.
            'serial_bridge_node = autotargeting_serial_bridge.serial_bridge_node:main',
        ],
    },
)
