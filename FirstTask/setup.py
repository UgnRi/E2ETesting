from setuptools import setup, find_packages

setup(
    name="wireless_ap_test",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'playwright>=1.35.0',
        'asyncssh>=2.13.1',
        'python-json-logger>=2.0.7',
    ],
)