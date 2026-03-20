from setuptools import setup, find_packages

setup(
    name="myai-sdk",
    version="2.0.0",
    description="MyAI Agent Developer Kit — autonomous agent-to-agent GPU compute",
    packages=find_packages(),
    install_requires=["httpx>=0.24.0"],
    extras_require={"langchain": ["langchain>=0.1.0"]},
    python_requires=">=3.9",
)
