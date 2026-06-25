from setuptools import setup, find_packages

setup(
    name="sir9tui",
    version="1.0.0",
    description="sir9tui — AI STEM Tutor by Nenifix",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Godwin Appiah (Neni)",
    author_email="info@nenifix.com",
    url="https://github.com/nenifix/sir9tui-v1",
    packages=find_packages(),
    package_data={
        "": ["app.tcss", "*.json", "*.db"],
    },
    install_requires=[
        "textual>=0.62",
        "rich>=13.3.3",
    ],
    entry_points={
        "console_scripts": [
            "sir9tui=sir9tui.app:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.11",
)
