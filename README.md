# PyJoern

## Install

The Python frontend depends on two native backends:
1. Java 17
2. Graphviz

You must have these installed on your machine before pip installing this library.

```bash
pip3 install -e .
```

## Usage

```python 
from pyjoern import fast_cfgs_from_source

cfgs = out = fast_cfgs_from_source("tests/source/simple.c")
main_func = cfgs["main"]
print(main_func.edges)
```