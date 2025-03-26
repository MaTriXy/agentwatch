from setuptools import find_packages, setup

setup(
    name='spyllmn',
    version='1.0.0',
    author='Shai Dvash',
    author_email='shai.dvash@cyberark.com',
    description='Platform agnostic Agentic AI runtime observability framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/cyberark/spyllm',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    install_requires=[

    ],
)