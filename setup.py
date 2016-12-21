from distutils.core import setup

VERSION = '0.0.11'


setup(
    name='fosslint',
    version=VERSION,
    description="FOSS Policy Checker Tool",
    long_description="""
    fosslint checks the structure of free software projects so that they follow
    a given policy.
    """,
    author='John-John Tedro',
    author_email='udoprog@tedro.se',
    url='http://github.com/udoprog/fosslint',
    license='GPLv3',
    packages=[
        'fosslint',
        'fosslint.licenses',
        'fosslint.policies',
        'fosslint.extensions'
    ],
    scripts=['bin/fosslint'],
    install_requires=[],
    package_data={
        'fosslint.licenses': ['*.txt']
    }
)
