from setuptools import setup

package_name = 'rqt_power'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    package_dir={'': 'src'},
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name + '/resource', ['resource/mainwindow.ui']),
        ('share/' + package_name + '/resource', ['resource/AUV8.1_Top.png']),
        ('share/' + package_name + '/resource', ['resource/AUV8.1_Top_filaire_transparent_Rotate.png']),
        ('share/' + package_name + '/resource', ['resource/LITE1_Top.png']),
        ('share/' + package_name + '/resource', ['resource/LITE1_Top_filaire_transparent_Rotate.png']),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['plugin.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Software Team',
    maintainer='Software Team',
    maintainer_email='log.club.sonia@etsmtl.net',
    keywords=['ROS2', 'RQT'],
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

