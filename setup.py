from setuptools import setup, find_packages

setup(
    name="pybilibilimusic",
    version="1.0.0",
    packages=find_packages(where="cli/src"),
    package_dir={"": "cli/src"},
    python_requires=">=3.7",
)

