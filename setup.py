import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Reloadrable",
    version="1.0.0",
    author="Yuta Urushiyama",
    author_email="aswif10flis1ntkb@gmail.com",
    description="Reloadr's hot-reloading Python code + a bunch of little extensions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/urushiyama/reloadrable",
    packages=setuptools.find_packages(),
    license="LGPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    python_requires=">=3.7",
    install_requires=[
        "watchdog",
    ],
    include_package_data=True,
)
