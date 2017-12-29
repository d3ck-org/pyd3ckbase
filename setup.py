# https://marthall.github.io/blog/how-to-package-a-python-app/
# https://github.com/pypa/sampleproject

from setuptools import setup, find_packages

setup(
    name='pyd3ckbase',
    version='0.0.1',
    description='pyd3ckbase: Test project, do not use in production!',
    packages=find_packages(exclude=['examples']),
    install_requires=[
        'python-dateutil>=2.6.0',
        'pytz>=2016.7',
        'PyYAML>=3.12',
        'coloredlogs>=5.2',
        'pendulum>=1.0.1',
        'termcolor>=1.1.0'
    ]
)
