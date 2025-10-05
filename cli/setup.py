from setuptools import setup, find_packages
import os

# read README.md as a longer description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# read requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# get version information
def get_version():
    init_file = os.path.join(os.path.dirname(__file__), "src", "__init__.py")
    with open(init_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="pybilimusic",
    version=get_version(),
    author="pybilibilimusic",
    author_email="shanghai_chengren@126.com",
    description="A CLI interface to download Bilibili videos and convert them to MP3 format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pybilibilimusic/pybilimusic",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pybilimusic_CLI=main_CLI:main",
        ],
    },
    keywords="bilibili, download, video, mp3",
    project_urls={
        "Bug Reports": "https://github.com/pybilibilimusic/pybilimusic/issues",
        "Source": "https://github.com/pybilibilimusic/pybilimusic",
    },
)
