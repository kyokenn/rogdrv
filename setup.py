#!/usr/bin/env python

from setuptools import setup

readme = open('README.md').read()

setup(
    name='rogdrv',
    version='0.0.1',
    description='ASUS ROG userspace driver',
    url='https://github.com/kyokenn/rogdrv',
    author='Kyoken',
    author_email='kyoken@kyoken.ninja',
    license='GPL',
    long_description=readme,
    entry_points={
        'console_scripts': ['rogdrv=rogdrv.__main__:main']
    },
    packages=[
        'rogdrv',
    ],
    install_requires=['hidapi-cffi>=0.2.1', 'evdev==0.4.7'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GPL License',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment',
    ]
)
