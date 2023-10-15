# PyJoern
A Python frontend and lifter for Joern API, focused on CFG manipulation. 

## Install
The Python frontend depends on two native backends: Java 17 and Graphviz.
You must have these installed on your machine before pip installing this library.
You also need to install [cfgutils](https://github.com/mahaloz/cfgutils). 
To install everything in a working condition, do the following for Ubuntu:

```bash
sudo apt-get install -y openjdk-17-jdk graphviz-dev
git clone https://github.com/mahaloz/cfgutils
pip3 install -e ./cfgutils
git clone https://github.com/mahaloz/pyjoern
pip3 install -e ./pyjoern 
```

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
The current version of PyJoern can be found in [pyjoern/__init__.py](./pyjoern/__init__.py) as `__version__`.
The last decimal point in the version is the PyJoern-specific update. 
The first three are the current version of Joern that PyJoern is supporting. 

For instance:
```python 
__version__ = "v1.2.18.1"
```

This would mean Joern version `v1.2.18`, with PyJoern update `1`. 
