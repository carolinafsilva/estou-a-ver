from setuptools import setup, Extension

setup(name='estouaver', version='1.0', license='MIT',
      ext_modules=[Extension('estouaver', ['src/estou-a-ver.c'])],
      install_requires=['python-daemon'])
