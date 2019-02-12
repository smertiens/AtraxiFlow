from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='atraxi-flow',
    version='1.0.0',
    packages=['nodes', 'nodes.graphics', 'common'],
    package_dir={'': 'src'},
    url='https://github.com/smertiens/AtraxiFlow',
    license='AGPL-3.0',
    author='Sean Mertiens',
    author_email='sean@atraxi-flow.com',
    description='The flexible python workflow tool',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
