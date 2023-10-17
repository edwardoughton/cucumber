# Techno-Economic Assessment of Mobile Broadband

This repository holds the code for a global model capable of evaluating different mobile broadband strategies.

Using conda
===========

You can install the existing conda environment using:

    conda env create -f environment.yml
    
Otherwise, you can create one from scratch:

    conda create --name cuba python=3.7 gdal

Once you've completed either optionm you can activate your environment (and run this each time you switch projects):

    conda activate cuba

Some packages will be required if you didn't use the pre-existing conda environment:

    conda install geopandas rasterio rasterstats

Getting Started
============

To begin running the code, we first need to collect the data:

    python scripts/collect_data.py

And then process the demand inputs:

    python scripts/demand.py

Next, we can preprocess other required data:

    python scripts/preprocess.py

Before identifying local sites:

    python scripts/supply.py

The energy layers also need processing:

    python scripts/energy.py


Contributors
============
- Ed Oughton (George Mason University)
