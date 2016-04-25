from setuptools import setup

setup(
    name="Proog",
    version="0.0.1",
    description="A mail server framework",
    install_requires=[
        "dnspython3>=1.12.0",
        "aiosmtpd",
    ],
    license="GPLv3 or later",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Topic :: Communications :: Email",
    ],
)
