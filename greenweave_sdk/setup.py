"""
GreenWeave SDK — pip install setup
Run: pip install -e .   (from the greenweave_sdk folder)
"""

from setuptools import setup, find_packages

setup(
    name="greenweave-sdk",
    version="1.0.0",
    description="Drop-in OpenAI SDK replacement with carbon-aware routing",
    long_description="""
GreenWeave SDK makes any OpenAI-powered app carbon-aware with one line change.

Change:
    from openai import OpenAI

To:
    from greenweave_sdk import GreenWeave as OpenAI

That's it. Every AI call is now:
- Carbon-routed to the most efficient model for current grid conditions
- Semantically cached (repeat queries = 0 CO2, ~2ms)
- ESG-logged for compliance reporting
- Budget-tracked with automatic model downgrade
    """,
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.28.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="openai carbon-aware sustainability ai routing green",
    author="GreenWeave Team",
    author_email="team@greenweave.ai",
    project_urls={
        "Source": "https://github.com/Guruprasad0818/greenweave",
    },
)
