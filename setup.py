#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Ivan Georgiev",
    author_email='ivan.georgiev@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="Authorization Helper for Python projects",
    long_description_content_type="text/x-rst",
    install_requires=requirements,
    license="BSD license",
    long_description=open('README.rst'),
    include_package_data=True,
    keywords='pigauth',
    name='pigauth',
    packages=find_packages(include=['pigauth', 'pigauth.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ivangeorgiev/pigauth',
    version='0.3.0',
    zip_safe=False,
    project_urs={
        'Documentation': 'https://pigauth.readthedocs.io/',
        'GitHub': 'https://github.com/ivangeorgiev/pigauth',
    }
)
