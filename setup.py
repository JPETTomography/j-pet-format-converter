import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="converter-JPET",
    version="2.0.0",
    author="Mateusz Kruk, Rafał Masełek",
    author_email="krukm634@gmail.com",
    description="This is a interfile to dicom converter created by Mateusz Kruk and Rafal Maselek.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JPETTomography/j-pet-format-converter",
    project_urls={
        "Bug Tracker": "https://github.com/JPETTomography/j-pet-format-converter/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apache License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)