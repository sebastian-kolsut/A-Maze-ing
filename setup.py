from setuptools import setup


setup(
    name="mazegen",
    version="1.0.0",
    packages=["mazegen"],
    install_requires=[],
    author="Dawid Gajownik, Sebastian Kolsut",
    description="A standalone module for generating and solving mazes.",
    long_description=open("mazegen/README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
