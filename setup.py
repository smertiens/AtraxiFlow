import os
import setuptools

basepath = os.path.dirname(__file__)
basepath += '/' if basepath != '' else ''

with open(basepath + "README.md", "r") as fh:
    long_description = fh.read()

with open(basepath + 'requirements.txt', 'r') as fh:
    requirements = fh.readlines()

setuptools.setup(
    name='atraxi-flow',
    version='2.0.0a1',
    packages=setuptools.find_packages(basepath + 'src'),
    package_dir={'': basepath + 'src'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    url='https://atraxi-flow.com',
    project_urls={
        'Documentation': 'https://docs.atraxi-flow.com/',
        'Github': 'https://github.com/smertiens/AtraxiFlow',
    },
    keywords='workflow automation nodebased flow',
    license='AGPL-3.0',
    author='Sean Mertiens',
    author_email='sean@atraxi-flow.com',
    description='The flexible Python workflow tool',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    python_requires='>=3.5',

    package_data={
        'atraxiflow': ['creator/assets/*', 'base/assets/*', 'templates/*'],
    },

    entry_points={
        'console_scripts': [
            'atraxi-flow=atraxiflow.atraxiflow_cli:main',
        ]
    }
)
