from setuptools import setup


setup(
    name="simple-versioner",
    # Because I want to keep versioner a single module to be copied over, I
    # sadly cannot use simple-versioner to version simpler-versioner :)
    version="0.1.0",
    author="David Cournapeau",
    author_email="cournape@gmail.com",
    description="Simple versioning module for python packages.",
    license="MIT",
    url="https://github.com/cournape/simple-versioner",
    py_modules=["simple_versioner"],
)
