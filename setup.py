#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "tabulate",
]

setup(
    name='putshebang',
    version='0.1.5',
    description="A small tool that helps in adding the appropriate shebang",
    long_description=readme + '\n\n' + history,
    author="Fady Adel",
    author_email='2masadel@gmail.com',
    url='https://github.com/faddyy/putshebang',
    packages=find_packages(include=['putshebang']),
    entry_points={
        'console_scripts': [
            'putshebang=putshebang.__main__:main'
        ]
    },
    platforms=["unix"],
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='putshebang add put shebang',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
)
