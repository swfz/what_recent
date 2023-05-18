import os
from setuptools import setup, find_packages

setup(
    name='what_recent',
    version='0.0.1',
    description='summarize recent activity in GitHub',
    author='swfz',
    author_email='sawafuji.09@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=['openai','requests'],
    entry_points={
        "console_scripts": [
            "what_recent=what_recent.main:main",
        ]
    }
)
