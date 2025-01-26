from setuptools import setup, find_packages


# Safely read the version from obsidianknittrpy/__init__.py
def get_version():
    version = None
    with open("obsidianknittrpy/__init__.py", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"')
                break
    if version is None:
        raise RuntimeError(
            "Unable to find version string in obsidianknittrpy/__init__.py"
        )
    return version


# Safely read the long description from README.md
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="obsidian_knittr_py",  # Package name
    version=get_version(),  # Use version from __init__.py
    packages=find_packages(include=["obsidianknittrpy", "obsidianknittrpy.*"]),
    install_requires=[
        "appdirs==1.4.4",
        "obsidianhtml==4.0.1",
        "pyperclip==1.9.0",
        "PyYAML==6.0.2",
        "setuptools==75.8.0",
        "tkcalendar==1.6.1",
    ],
    extras_require={"dev": ["pipreqs", "black"]},
    entry_points={
        "console_scripts": [
            "obsidianknittrpy=obsidianknittrpy.main:main",  # entry-point for obsidianknittrpy
            "okpy=obsidianknittrpy.main:main",  # entry-point shorthand
        ],
    },
    author="Gewerd Strauss",
    author_email="/",  # Replace with a valid email address
    description="A WIP port of https://github.com/Gewerd-Strauss/ObsidianKnittr",
    long_description=long_description,  # Use the long description read from README.md
    long_description_content_type="text/markdown",
    url="https://github.com/Gewerd-Strauss/obsidian_knittr_py",  # Project URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.6",  # Minimum Python version requirement
)
