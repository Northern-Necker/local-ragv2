from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="local-ragv2",
    version="2.0.0",
    description="Enhanced document analysis with Azure Document Intelligence and Knowledge-Augmented Graph RAG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Organization",
    author_email="contact@example.com",
    url="https://github.com/yourusername/local-ragv2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'black>=23.0.0',
            'isort>=5.12.0',
            'mypy>=1.0.0',
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.1.0'
        ],
        'docs': [
            'sphinx>=4.5.0',
            'sphinx-rtd-theme>=1.0.0',
            'sphinx-autodoc-typehints>=1.18.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'ragv2-process=src.cli.process:main',
            'ragv2-query=src.cli.query:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Text Processing :: General'
    ],
    project_urls={
        'Documentation': 'https://local-ragv2.readthedocs.io/',
        'Source': 'https://github.com/yourusername/local-ragv2',
        'Issues': 'https://github.com/yourusername/local-ragv2/issues'
    }
)
