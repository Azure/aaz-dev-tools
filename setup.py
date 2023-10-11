from setuptools import find_packages, setup
from version import VERSION


def read_requirements(filename: str):
    with open(filename) as requirements_file:
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


# # version.py defines the VERSION and VERSION_SHORT variables.
# # We use exec here, so we don't import cached_path whilst setting up.
# VERSION = {}  # type: ignore
# with open("version.py", "r") as version_file:
#     exec(version_file.read(), VERSION)

with open("README.md", "r", encoding="utf-8") as fp:
    README = fp.read()
with open("HISTORY.rst", "r", encoding="utf-8") as fp:
    HISTORY = fp.read()


setup(
    name='aaz-dev',
    version=VERSION,
    description='Microsoft Atomic Azure CLI Commands Developer Tools',
    long_description=README,
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],
    keywords="azure",
    url="https://github.com/Azure/aaz-dev-tools",
    author="Microsoft Corporation",
    author_email="azpycli@microsoft.com",
    license='MIT',
    package_dir={
        "": "src"
    },
    packages=find_packages(
        where="src",
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"],
    ),
    include_package_data=True,
    install_requires=read_requirements("requirements.txt"),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": ["aaz-dev=aaz_dev.app.main:main"]
    },
)
