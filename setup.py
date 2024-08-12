from setuptools import setup

VERSION = '0.0.1'
DESCRIPTION = 'Receive messages at a specific time'
LONG_DESCRIPTION = 'Receive messages at a specific time over sockets.'

setup(
    name="Pumpduler",
    version=VERSION,
    author="Harkishan Khuva",
    author_email="harkishankhuva@proton.me",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    install_requires=[],
    python_requires=">3.10.11",
    license="MIT",
    url="https://github.com/hakiKhuva/pumpduler",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10"
    ]
)