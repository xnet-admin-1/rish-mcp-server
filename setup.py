from setuptools import setup, find_packages

setup(
    name="rish-mcp-server",
    version="1.0.0",
    description="MCP server for Android system access via Shizuku",
    author="Josh Fordyce",
    author_email="admin@xnet.ngo",
    url="https://xnet.ngo",
    license="GPL-3.0",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "rish-mcp=src.server_direct:main",
        ],
    },
)
