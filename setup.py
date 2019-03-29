import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='atraxi-flow',
    version='1.0.0',
    packages=setuptools.find_packages('src'),
    package_dir={'':'src'},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
    description='The flexible python workflow tool',
    long_description=long_description,
    long_description_content_type="text/markdown",

    python_requires='>=3.4'
)