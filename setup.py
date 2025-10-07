"""
Setup script for Agentic AI Reasoning System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentic-reasoning-system",
    version="1.0.0",
    author="Your Team",
    author_email="your.email@example.com",
    description="Multi-agent AI system for systematic logical reasoning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agentic-reasoning-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "sympy>=1.12",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=24.0.0",
            "flake8>=7.0.0",
        ],
        "viz": [
            "matplotlib>=3.8.0",
            "plotly>=5.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "reasoning-demo=demo:main",
            "reasoning-api=backend.api:start_server",
        ],
    },
)
