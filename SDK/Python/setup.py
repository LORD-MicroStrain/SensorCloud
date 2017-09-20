'''
Created on Jul 15, 2014

@author: jonathan_herbst
'''

from distutils.core import setup
import sensorcloud

setup(name="SensorCloud API",
	version=sensorcloud.__version__,
	description="Python Programming Interface for SensorCloud",
	packages=["sensorcloud"],
	)
