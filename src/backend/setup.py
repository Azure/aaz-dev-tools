import os
from setuptools import find_packages, setup


def read_requirements(filename: str):
    with open(os.path.join(curr_path, filename)) as requirements_file:
        import re

        def fix_url_dependencies(req: str) -> str:
            """Pip and setuptools disagree about how URL dependencies should be handled."""
            m = re.match(
                r"^(git\+)?(https|ssh)://(git@)?github\.com/([\w-]+)/(?P<name>[\w-]+)\.git", req
            )
            if m is None:
                return req
            else:
                return f"{m.group('name')} @ {req}"

        requirements = []
        for line in requirements_file:
            line = line.strip()
            if line.startswith("#") or len(line) <= 0:
                continue
            requirements.append(fix_url_dependencies(line))
    return requirements


# version.py defines the VERSION and VERSION_SHORT variables.
# We use exec here, so we don't import cached_path whilst setting up.
VERSION = {}  # type: ignore
with open(os.path.join(os.getcwd(), "scripts", "version.py"), "r") as version_file:
    exec(version_file.read(), VERSION)

curr_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(curr_path, "README.rst"), "r", encoding="utf-8") as fp:
    README = fp.read()
with open(os.path.join(curr_path, "HISTORY.rst"), "r", encoding="utf-8") as fp:
    HISTORY = fp.read()

setup(
    name="aaz-dev",
    version=VERSION["VERSION"],
    description="Microsoft Atomic Azure CLI Commands Developer Tools",
    long_description=README + "\n\n" + HISTORY,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="azure",
    url="https://github.com/kairu-ms/aaz-dev-tools",
    author="Microsoft Corporation",
    author_email="azpycli@microsoft.com",
    license="MIT",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"],
    ),
    include_package_data=True,
    install_requires=read_requirements("requirements.txt"),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["aazdev=aazdev.main:main"]
    },
)
