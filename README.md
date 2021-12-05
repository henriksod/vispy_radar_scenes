# RadarScenes Tools

## About
![viewer example](https://github.com/henriksod/vispy_radar_scenes/blob/master/doc/viewer.PNG?raw=true)

This python package provides fast visualization for the [RadarScenes](http://radar-scenes.com) dataset. 

The Open GL based visualizer is smoother than oleschum/radar_scenes, but has some functionality stripped off to be more suitable for
an online visualization setting.

## Installation

The package is designed for Python versions `>=3.8`.

Navigate to the repo root:
```
cd vispy_radar_scenes
```

Install inside your virtual environment using:
```
pip install .
```
or
```
python setup.py install
```

### Virtual Environment
It is *highly recommended* to install the package in its own virtual environment. To do so, create a virtual environment 
prior to installation of the package:

```
python3 -m venv ~/.virtualenvs/radar_scenes
```
This will create a python virtual environment called `radar_scenes` in the folder `.virtualenvs` in your home directory.

This environment can be activated via
```
source ~/.virtualenvs/radar_scenes/bin/activate
```
An active virtual environment is indicated by a preceding `(radar_scenes)` line before the usual bash prompt.

Once the virtual environment is active, the package can be installed with the command

```
cd vispy_radar_scenes
pip install .
```

## Citation
Please refer to www.radar-scenes.com to get instructions on how to cite the data set. 


## Usage

After successful installation, the `vispy_radar_scenes` package is available in your python environment.

### Radar Data Viewer
During installation, the command `rad_viewer` is made available. If you have installed the package into a virtual
environment, this command is only available while the virtual environment is active.

Calling `vispy_rad_viewer` launches the radar data viewer. As an optional command line argument, a path to a `*.json` file 
from the RadarScenes dataset can be provided. The sequence will then be loaded directly on start up.

Example:
```
(radar_scenes)
$ vispy_rad_viewer ~/datasets/radar_scenes/data/sequence_128/scenes.json
```

The time slider itself or the arrow keys on your keyboard can be used to scroll through the sequence.

## License
This project is licensed under the terms of the MIT license.

Notice, however, that the RadarScenes data set itself comes with a different license.
