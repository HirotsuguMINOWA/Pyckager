from Cython.Distutils import build_ext
from setuptools import setup, Extension

ext_modules = [
    Extension('mypackage.hello', sources=['sample3_kivy.py'])
]

setup(
    name='Sample App',
    #packages=['mypackage'],
    ext_modules=ext_modules,
    cmdclass={'build_ext': build_ext}
)
