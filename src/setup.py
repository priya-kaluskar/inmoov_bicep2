from setuptools import setup

package_name = 'py_bicep_angle_v2'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Andrew Banardi',
    maintainer_email='abanardi0@gmail.com',
    description='Bicep Angle Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'img_publisher = py_bicep_angle_v2.publisher:main',
            'img_subscriber = py_bicep_angle_v2.subscriber:main',
        ],
    },
)
