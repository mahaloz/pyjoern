# PyJoern
A Python frontend and lifter for Joern API, focused on CFG manipulation. 

## Install
The Python frontend depends on two native backends: Java 19 and Graphviz.
You must have these installed on your machine before pip installing this library.
To install everything in a working condition, do the following for Ubuntu:

```bash
sudo apt-get install -y openjdk-19-jdk graphviz-dev
pip3 install pyjoern && pyjoern --install
```

When you run `pyjoern --install` (which should be in your path after pip install), it wil download the latest Joern binaries and install them 
inside the Python package.

## Usage
Use PyJoern as a library for lifting source into a CFG. 
The IL the source is lifted to is described in [JIL](./pyjoern/cfg/jil/statement.py).

```python 
from pyjoern import fast_cfgs_from_source

cfgs = fast_cfgs_from_source("tests/source/simple.c")
main_func = cfgs["main"]
print(main_func.edges)
```

## Versioning
The current version of PyJoern can be found in [pyjoern/\_\_init\_\_.py] as `__version__`.
The point in the version is the PyJoern specific updates. 
The first three are the current version of Joern that PyJoern is supporting. 

For instance:
```python 
__version__ = "v1.2.18.1"
```

This would mean Joern version `v1.2.18`, with PyJoern update `1`. 
