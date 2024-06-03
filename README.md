# Sustainability assessment of global universal mobile broadband strategies 

This repository estimates the global emissions impacts of  
different universal mobile broadband strategies (focusing on terrestrial 
4G and 5G).

Sustainable Development Goal (SDG) 9 aims to build resilient infrastructure and 
promote inclusive and sustainable industrialization. For example, via universal 
mobile broadband. 

However, there is a trade-off in attempting to deliver this aspirational 
objective. Expanding existing broadband infrastructure will incur new emissions, 
potentially contrevening SDG13, which aims to take urgent steps to combat 
climate change and its impacts via decarbonization.

This analysis quantifies this trade-off by first estimating (i) the existing 
energy and emissions produced globally by mobile broadband networks, (ii) the 
additional energy and emissions impacts from providing universal mobile 
broadband via terrestrial 4G or 5G, and then (iii) the energy and emissions 
savings from utilizing infrastructure sharing. 

Reference
===========

Oughton, E.J., Oh, J., Ballan, S., Kusuma, J., 2023. Sustainability assessment 
of 4G and 5G universal mobile broadband strategies. https://doi.org/10.48550/arXiv.2311.05480


Installation using conda
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
