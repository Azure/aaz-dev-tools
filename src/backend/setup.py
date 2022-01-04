from setuptools import setup

VERSION = "0.0.1"

setup(
    name='aaz-dev-tools',
    version=VERSION,
    description='Microsoft Azure CLI Atomic Commands Developer Tools',
    license='MIT',
    entry_points={
        'console_scripts': [
            'aazdev=aazdev.main:main'
        ],
    },
)