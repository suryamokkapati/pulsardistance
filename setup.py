from setuptools import setup

setup(
    name="pulsardistance",
    version="2.0.0",
    description="CLI utility to estimate pulsar distances using full YMW16 and NE2001 models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    py_modules=["pulsardistance"],
    python_requires=">=3.7",
    install_requires=[
        "pygedm",
        "astropy",
    ],
    entry_points={
        "console_scripts": [
            "pulsardistance=pulsardistance:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Intended Audience :: Science/Research",
    ],
)
