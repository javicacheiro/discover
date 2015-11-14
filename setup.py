from setuptools import setup

setup(
    name='discover',
    version='0.1',
    packages=['discover'],
    include_package_data=True,
    install_requires=[
        'click',
        'PyYAML',
    ],
    entry_points='''
        [console_scripts]
        discover=discover.cli:cli
    '''
)
