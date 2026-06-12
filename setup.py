from setuptools import find_packages, setup


setup(
    name="de-mentor",
    version="0.1.0",
    description="Self-service data engineering mentorship labs and lesson artifacts.",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[],
    extras_require={"dev": ["pytest>=8.0,<9.0"]},
    entry_points={"console_scripts": ["mentor-lab=mentor_lab.cli:console"]},
    python_requires=">=3.9",
)

