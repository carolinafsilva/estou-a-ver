from distutils.core import setup, Extension

setup(name='estouaver', version='1.0',
      ext_modules=[Extension('estouaver', ['estou-a-ver/estou-a-ver.c'])])
