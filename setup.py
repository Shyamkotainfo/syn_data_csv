
from setuptools import setup, find_packages

setup(
    name='syn_data_gen',
    version='0.1.0',
    author='Info Services',
    author_email='infoservices.com',
    description='A package to generate synthetic data using LLMs.',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/syn_data_gen',  # Add your GitHub repo link
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'generate-synthetic-data=syn_data_gen.app.main:main',  # CLI entry point
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
