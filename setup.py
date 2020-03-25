#!/bin/env/python
# pylint: disable=C0111
import distutils.cmd
import distutils.log
from distutils.core import setup
import os
from glob import glob
import subprocess
from setuptools import find_packages
import setuptools.command.build_py
import setuptools.command.develop

ANTLR_VERSION = "4.8"
ANTLR_RT = "antlr4-python3-runtime == {}".format(ANTLR_VERSION)


def findAntlr():
    """Try to find the ANTLR .jar-file."""
    if os.environ.get("APPVEYOR"):
        classpath = r"c:\projects\pya2l\antlr-4.8-complete.jar"
    else:
        classpath = os.getenv("CLASSPATH")
        classpath = classpath if classpath is not None else ""

    if "antlr" not in classpath.lower():
        raise OSError("Could not locate ANTLR4 jar in 'CLASSPATH'.")
    else:
        for pt in classpath.split(os.pathsep):
            if "antlr" in pt.lower():
                antlrJar = pt

                break

    if not ANTLR_VERSION in antlrJar:
        raise ValueError(
            "pyA2L requires Antlr {0} -- found '{1}'".format(ANTLR_VERSION, antlrJar)
        )

    if not os.path.exists(antlrJar):
        raise FileNotFoundError("ANTLR4 not found: {0}".format(antlrJar))

    return antlrJar


class AntlrAutogen(distutils.cmd.Command):
    """Custom command to autogenerate Python code using ANTLR."""

    description = "generate python code using antlr"
    user_options = [
        ("target-dir=", None, "(optional) output directory for antlr artifacts"),
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Must be snake_case; variable created from user_options.
        # pylint: disable=C0103
        self.target_dir = None

    def finalize_options(self):
        """Post-process options."""
        a2lGrammar = os.path.join("pya2l", "a2l.g4")
        amlGrammar = os.path.join("pya2l", "aml.g4")
        # distutils.cmd.Command should not have __init__().
        # pylint: disable=W0201
        self.arguments = [a2lGrammar, amlGrammar, "-Dlanguage=Python3"]

        if self.target_dir is not None:
            self.arguments.extend(["-o", self.target_dir])

    def run(self):
        """Run ANTLR."""
        antlrPath = findAntlr()
        antlrCmd = ["java", "-Xmx500M", "-cp", antlrPath, "org.antlr.v4.Tool"]
        self.announce(" ".join(antlrCmd + self.arguments), level=distutils.log.INFO)
        subprocess.check_call(antlrCmd + self.arguments)
        clean()


def clean():
    """Remove unneeded files."""
    tokens = glob(os.path.join("pya2l", "*tokens"))
    interp = glob(os.path.join("pya2l", "*interp"))
    listener = [
        glob(os.path.join("pya2l", i + "Listener.py"))[0] for i in ["a2l", "aml"]
    ]

    for unneeded in tokens + interp + listener:
        os.remove(unneeded)


# pylint: disable=R0901
class CustomBuildPy(setuptools.command.build_py.build_py):
    """Extended build_py which also runs ANTLR."""

    def run(self):
        self.run_command("antlr")
        super().run()


class CustomDevelop(setuptools.command.develop.develop):
    """Extended develop which also runs ANTLR"""

    def run(self):
        self.run_command("antlr")
        super().run()


INSTALL_REQS = [ANTLR_RT, "mako", "six", "SQLAlchemy", "sortedcontainers"]

with open(os.path.join("pya2l", "version.py"), "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[-1].strip().strip('"')
            break

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name="pya2l",
    version=version,
    description="A2L for Python",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Christoph Schueler",
    author_email="cpu12.gems@googlemail.com",
    url="https://www.github.com/Christoph2/pyA2L",
    cmdclass={
        "antlr": AntlrAutogen,
        "build_py": CustomBuildPy,
        "develop": CustomDevelop,
    },
    packages=find_packages(),
    install_requires=INSTALL_REQS,
    tests_require=["pytest", "pytest-runner"],
    test_suite="pya2l.tests",
    license="GPLv2",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
