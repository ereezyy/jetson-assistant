"""
Setup script for the Jetson TX1 Personal Assistant.
"""

import os
from setuptools import setup, find_packages

# Read the contents of requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read the README for the long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="jetson-assistant",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A personal assistant for the NVIDIA Jetson TX1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jetson-assistant",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Home Automation",
        "Topic :: Desktop Environment",
    ],
    entry_points={
        "console_scripts": [
            "jetson-assistant=assistant:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/jetson-assistant/issues",
        "Source": "https://github.com/yourusername/jetson-assistant",
    },
)
