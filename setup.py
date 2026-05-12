from setuptools import setup, find_packages

setup(
    name="myai-sdk",
    version="2.1.0",
    description="MyAI SDK — OpenAI-compatible client + Agent Developer Kit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/myaitoken/myai-sdk",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.24.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "langchain": ["langchain>=0.1.0", "openai>=1.0.0"],
        "all": ["openai>=1.0.0", "langchain>=0.1.0"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
