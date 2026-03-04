from setuptools import setup

setup(
    name="pulsardistance",
    version="1.0.0",
    description="CLI utility to estimate pulsar distances from RA, DEC, and DM",
    py_modules=["pulsardistance"],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "pulsardistance=pulsardistance:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
)
