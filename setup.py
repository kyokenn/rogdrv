#!/usr/bin/env python3

from setuptools import setup

readme = open('README.md').read()

setup(
    name='rogdrv',
    version='0.1.0',
    description='ASUS ROG Mouse Driver',
    url='https://github.com/kyokenn/rogdrv',
    author='Kyoken',
    author_email='kyoken@kyoken.ninja',
    license='GPL',
    long_description=readme,
    entry_points={
        'console_scripts': [
            'rogdrv=rog.__main__:rogdrv',
            'rogdrv-config=rog.__main__:rogdrv_config',
        ]
    },
    packages=[
        'rog',
    ],
    data_files=[
        ['share/applications', ['rogdrv.desktop']],
        ['share/pixmaps', ['rog/rog.png']],
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GPL License',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment',
    ],
    setup_requires=[
        'hid',
    ],
    include_package_data=True,
    zip_safe=False,
)
