"""Copyright 2022 by @doldam0. All rights reserved."""

import setuptools


if __name__ == "__main__":
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

    with open("requirements.txt", "r") as f:
        setuptools.setup(
            name="clsarg",
            version="0.0.3",
            author="doldam0",
            author_email="jinustar@g.skku.edu",
            description="The class-based argument parser",
            long_description=long_description,
            long_description_content_type="text/markdown",
            url="https://github.com/doldam0/clsarg",
            classifiers=[
                "Programming Language :: Python :: 3",
                "Operating System :: OS Independent",
            ],
            packages=setuptools.find_packages(
                exclude=("test", "build", "dist", "scripts")
            ),
            python_requires=">=3.8",
            install_requires=[
                pkgs.strip()
                for pkgs in f.readlines()
                if not pkgs.startswith("--")
            ],
        )
