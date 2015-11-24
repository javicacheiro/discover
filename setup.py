from setuptools import setup, find_packages

setup(
    name='discover',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'PyYAML',
        'Jinja2',
        'snimpy',
    ],
    entry_points='''
        [console_scripts]
        discover=discover.cli:cli
    '''
)
