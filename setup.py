import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("development/Require/requirements.txt") as f:
    required = f.read().splitlines()

with open("VERSION", "r") as fh:
    version = fh.read().strip()

setuptools.setup(
    name="r5",
    version=version,
    description="R5 Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(include="r5.*"),
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=required,
    entry_points={"console_scripts": ["r5 = r5.Main:cli.run"]},
)