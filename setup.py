"""Setup."""
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='tap-wordpress-plugin-stats',
    version='0.1.0',
    description='Singer.io tap for extracting data from WordPress Plugin Stats',
    author='Stitch',
    url='https://github.com/Yoast/singer-tap-wordpress-plugin-stats',
    classifiers=['Programming Language :: Python :: 3 :: Only'],
    py_modules=['tap_wordpress_plugin_stats'],
    install_requires=[
        'httpx[http2]~=0.17.0',
        'singer-python~=5.12.0',
    ],
    entry_points="""
        [console_scripts]
        tap-wordpress-plugin-stats=tap_wordpress_plugin_stats:main
    """,
    packages=find_packages(),
    package_data={
        'tap_wordpress_plugin_stats': [
            'schemas/*.json',
        ],
    },
    include_package_data=True,
)
