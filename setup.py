from setuptools import setup

setup(
    name="rebase",
    version="0.1",
    description="Rebase is a CLI app for Fedora and other RHEL-based distributions. It's made to make Fedora and similar distros more reproducible.",
    py_modules=["main", "config_save"],
    entry_points={
        'console_scripts': [
            'rebase=main:main',
        ],
    },
)