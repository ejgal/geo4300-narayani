#!/bin/bash -x
pytest
python convert.py
python plot.py
python plot_stations.py
cd ../latex
make -B
cd ../
./delivery.sh
