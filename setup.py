from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="can_uds",
    version="0.0.1",
    packages=find_packages(),
    install_requires=required,
    author="laysakura",
    author_email="lay.sakura@gmail.com",
    description="A package for CAN UDS communication",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/laysakura/can-uds-junkbox",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.9",
)
