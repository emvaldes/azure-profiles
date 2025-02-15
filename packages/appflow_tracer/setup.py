from setuptools import setup, find_packages

setup(
    name="appflow-tracer",  # Package name for pip install
    version="1.0.0",
    author="Eduardo Valdes",
    author_email="emvaldes@hotmail.com",
    description="Structured tracing system for Python applications",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/emvaldes/appflow-tracer",
    packages=find_packages(),  # Finds "appflow_tracer"
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],  # Add dependencies if needed
)
