#!/usr/bin/env python3

# Copyright (C) 2021 Kyoken, kyoken@kyoken.ninja

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from setuptools import setup

readme = open('README.md').read()

setup(
    name='rogdrv',
    version='0.3.0',
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
        'rog.device',
        'rog.ui',
    ],
    data_files=[
        ['share/applications', ['rogdrv.desktop']],
        ['share/pixmaps', ['rog/ui/rog-symbolic.symbolic.png']],
        ['share/pixmaps', ['rog/ui/rog.png']],
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GPL License',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment',
    ],
    include_package_data=True,
    zip_safe=False,
)
