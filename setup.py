"""Setup and install project_template

Typical usage:
  python setup.py develop
  python setup.py install
  python setup.py test
"""

import os
import setuptools
import setuptools.command.build_py
import setuptools.command.develop

from tools import gitsemver

module_folder = "project_template"

with open("README.md", encoding="utf-8") as file:
  longDescription = file.read()

with open("requirements.txt", encoding="utf-8") as file:
  required = file.read().splitlines()

version = gitsemver.get_version()
with open(f"{module_folder}/version.py", "w", encoding="utf-8") as file:
  file.write('"""Module version information\n"""\n\n')
  file.write(f'version = "{version}"\n')
  file.write(f'version_full = "{version.full_str()}"\n')

cwd = os.path.dirname(os.path.abspath(__file__))


def find_pyx(path="."):
  pyx_files = []
  for root, _, filenames in os.walk(path):
    for f in filenames:
      if f.endswith(".pyx"):
        pyx_files.append(os.path.join(root, f))
  return pyx_files


def find_cython_extensions(path="."):
  pyx_files = find_pyx(path)
  if len(pyx_files) == 0:
    return []
  import Cython  # pylint: disable=import-outside-toplevel
  extensions = Cython.Build.cythonize(pyx_files, language_level=3)
  if "numpy" in required:
    import numpy  # pylint: disable=import-outside-toplevel

    for ext in extensions:
      ext.include_dirs = [numpy.get_include()]
  return extensions


class BuildPy(setuptools.command.build_py.build_py):

  def run(self):
    setuptools.command.build_py.build_py.run(self)


class Develop(setuptools.command.develop.develop):

  def run(self):
    setuptools.command.develop.develop.run(self)


setuptools.setup(
    name="PythonProjectTemplate",
    version=str(version),
    description="A template repository for Python projects",
    long_description=longDescription,
    long_description_content_type="text/markdown",
    license="MIT",
    ext_modules=find_cython_extensions(),
    packages=setuptools.find_packages(),
    package_data={module_folder: []},
    install_requires=required,
    tests_require=[],
    test_suite="tests",
    scripts=[],
    author="Bradley Davis",
    author_email="me@bradleydavis.tech",
    url="https://github.com/WattsUp/PythonProjectTemplate",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    cmdclass={
        "build_py": BuildPy,
        "develop": Develop,
    },
    zip_safe=False,
)
