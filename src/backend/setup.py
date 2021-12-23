from setuptools import setup

setup(
    name='flask-my-extension',
    entry_points={
        'console_scripts': [
            'aazdev=app:cli'
        ],
    },
)