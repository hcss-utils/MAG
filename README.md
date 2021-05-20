# MAG

This repository contains **Microsoft Academic Knowledge API wrapper** that 
helps retrive information from Knowledge API. 


## Installation

### Local
To use or contribute to this repository, first checkout the code. Then create a new virtual environment:

```bash
$ git clone https://github.com/hcss-utils/MAG.git
$ cd MAG
$ python3 -m venv env
$ . env/bin/activate
```

Install the package and its dependencies
```bash
(env)$ python -m pip install --upgrade pip setuptools wheel
(env)$ python -m pip install -r requirements.txt
(env)$ python -m pip install -r requirements-dev.txt
(env)$ python -m pip install -e .
```

Alternatively, use `make`:
```bash
(env)$ make install-dev
```


### Google colab
To use this package from google colab, run:
```bash
!pip -q --no-cache-dir install git+https://github.com/hcss-utils/MAG.git
```

## Usage

To be updated.