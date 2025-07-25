# PyJoern
A Python frontend and lifter for Joern API, focused on CFG manipulation. 

## Install
This package requires you to have **Java 19, Graphviz, and Unzip** installed on your machine before running the
pip installer. In you don't have them on your system, use the [install_dependencies.sh](./install_dependencies.sh) 
script found in the source repo.

```
pip3 install pyjoern && pyjoern --install
```

Running `pyjoern --install` will init the Joern package for this first time, which will download the backend.

## Usage
Use PyJoern as a library for collecting info on source and getting a CFG. 
The IL the source CFG is lifted to is described in [JIL](./pyjoern/cfg/jil/statement.py).

```python 
from pyjoern import parse_source, fast_cfgs_from_source

# for full parsing
functions = parse_source("tests/source/simple.c")
main = functions["main"]
print(main.start_line)
print(main.cfg)

# for only the CFG
cfgs = fast_cfgs_from_source("tests/source/simple.c")
main_func = cfgs["main"]
print(main_func.edges)
```

See the [tests](./tests/tests.py) for more examples of how to use PyJoern.

## Versioning
The current version of PyJoern can be found in [pyjoern/\_\_init\_\_.py] as `__version__`.
The point in the version is the PyJoern specific updates. 
The first three are the current version of Joern that PyJoern is supporting. 

Example:
```python 
__version__ = "v1.2.18.1"
```

This would mean Joern version `v1.2.18`, with PyJoern update `1`. 
