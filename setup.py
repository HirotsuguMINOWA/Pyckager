import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
# def read(fname):
#     return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="src",  # PackageName,一般的な名前で，モジュールネームではない
    version="0.1",
    author="H.Minowa",
    python_requires='>=3.5',
    # author_email="",
    description="Packaging your python code into an one application with converting into native code.",  # ("aaa","bbb")
    license="BSD",
    keywords="example documentation tutorial",
    url=""  # "http://packages.python.org/an_example_pypi_project"
    # packages=find_packages('nativebuilder'),
    # packages=['native_app_builder']
    # , packages=['distribution', 'distribution/src', 'distribution/doc', 'distribution/test']
    , packages=find_packages()  # __init__.pyがあるフォルダ内を全て含めていく？
    # module name? fromコマンドから呼び出すのはこちらの名前．
    , package_dir={'src/*': ''}
    # , package_dir={'tmp': 'src'}
    # package_data = {'mypkg': ['data/*.dat']},
    # packages=['./'] #WARNING: './' not a valid package name; please use only .-separated package names in setup.py
    # ,long_description=read('README')
    , classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",  # TODO: 要修正
    ],
    entry_points={
        'console_scripts': [
            # e.g'command-name = package.module:main_func_name',
            # 'src = distribution.src:timeline_headquater',
            'src = src.main:entry_point_cli',  # call function main() in src
        ]
    }
    , install_requires=['Cython', 'PyInstaller', 'strenum', 'chardet']
    #, zip_safe=False  # エラー対策,指定すればエラー消える！？  #zip_safe=Trueにすると, 全てのファイルを単一の.egg(zipファイル)にまとめる
)
