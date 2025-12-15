from setuptools import setup, find_packages

setup(
    name='Apt-Updater',
    version='1.0.0',
    packages=find_packages(),
    py_modules=['aptUpdater'], # Tells setuptools to find the script
)
