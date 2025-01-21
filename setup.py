from setuptools import setup, find_packages

setup(
    name="obsidian_knittr_py",  # Package name
    version="0.1.9000",  # Version
    packages=find_packages(),  # Automatically find packages
    install_requires=[
        # List your dependencies here
        # e.g. 'requests', 'numpy', ...
    ],
    entry_points={
        "console_scripts": [
            "obsidianknittrpy=obsidianknittrpy.main:main",  # Replace with your entry point
            "okpy=obsidianknittrpy.main:main",  # Replace with your entry point
        ],
    },
    author="Gewerd Strauss",
    author_email="/",
    description="A WIP port of https://github.com/Gewerd-Strauss/ObsidianKnittr",
    long_description=open("README.md").read(),  # Long description from README.md
    long_description_content_type="text/markdown",
    url="https://github.com/Gewerd-Strauss/obsidian_knittr_py",  # Project URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version requirement
)
