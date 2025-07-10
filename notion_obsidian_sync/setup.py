#!/usr/bin/env python3
"""
Setup script for Notion ↔ Obsidian Sync
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="notion-obsidian-sync",
    version="1.0.0",
    author="RecursionLab",
    author_email="koryogden@gmail.com",
    description="Bidirectional sync between Notion and Obsidian with invisible intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/recursionlab/RecursionWhale",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "notion-obsidian-sync=sync_manager:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml", "*.md"],
    },
)

