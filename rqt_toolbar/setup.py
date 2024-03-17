from setuptools import setup

package_name = 'rqt_toolbar'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    package_dir={'': 'src'},
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name + '/resource', ['resource/battery.ui', 'resource/KillMission.ui', 'resource/palette.ui', 'resource/set_control_mode.ui', 'resource/start_cam.ui', 'resource/temp_sensor.ui', 'resource/warnings.ui']),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['plugin.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Dorian Scholz',
    maintainer='Dirk Thomas, Dorian Scholz, Austin Hendrix',
    maintainer_email='dthomas@osrfoundation.org',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description=(
    ),
    license='BSD',
    entry_points={
        'console_scripts': [
        ],
    },
)
