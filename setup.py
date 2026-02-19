from setuptools import setup, find_packages

setup(
    name="openclaw-monitor",
    version="1.0.0",
    description="OpenClaw Gateway 实时监控面板",
    author="Ryan",
    python_requires=">=3.7",
    packages=find_packages(),
    package_data={"": ["public/index.html"]},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "openclaw-monitor=server:main",
        ],
    },
)
