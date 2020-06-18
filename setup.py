import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='dlt2json',
    version='0.0.3',
    author='Riadh Abidi',
    author_email='riadh.abidi@outlook.com',
    description='convert a dlt file to json',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/r2b1d1/dlt2json',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires = [
        'logzero',
    ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    entry_points = {
        'console_scripts': [
            'dlt2json = dlt2json:main'
        ]
    }
)
