# MAG

This repository contains **Microsoft Academic Knowledge API wrapper** that 
helps retrive information from Knowledge API. 

Useful links:
* [evaluate endpoint](https://msr-apis.portal.azure-api.net/docs/services/academic-search-api/operations/565d753be597ed16ac3ffc03?)
* [paper entity attributes](https://docs.microsoft.com/en-us/academic-services/project-academic-knowledge/reference-paper-entity-attributes)


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

```python
from mag import MAG

# create an instance of MAG class
organized_crime_publications = MAG(
    expr="And(And(AW='organized', AW='crime', Y=[2000, 2020]), Composite(F.FN='political science'))",
    key="2q3b955bfa210f9aa1a4eq35fa63378c",
)

# download data 
organized_crime_publications.download_publications()

# access data in json format
organized_crime_publications.json_data
# access data in tabular format
organized_crime_publications.table_data
```