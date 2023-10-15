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
```python 
from pyjoern import fast_cfgs_from_source

cfgs = out = fast_cfgs_from_source("tests/source/simple.c")
main_func = cfgs["main"]
print(main_func.edges)
```