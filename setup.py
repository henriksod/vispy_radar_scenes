import setuptools
import re

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version_line = open("src/vispy_radar_scenes/_version.py", "rt").read()
reg_ex_version = r"^__version__ = ['\"]([^'\"]*)['\"]"
res = re.search(reg_ex_version, version_line, re.M)
verstr = res.group(1)

install_requires = [
    "cycler==0.11.0",
    "freetype-py==2.2.0",
    "h5py==3.6.0",
    "hsluv==5.0.2",
    "kiwisolver==1.3.2",
    "matplotlib==3.3.4",
    "numpy==1.19.5",
    "Pillow==8.4.0",
    "pyparsing==3.0.6",
    "PyQt5==5.15.6",
    "PyQt5-Qt5==5.15.2",
    "PyQt5-sip==12.9.0",
    "pyqtgraph==0.12.3",
    "PySide2==5.15.2",
    "python-dateutil==2.8.2",
    "QDarkStyle==3.0.3",
    "QtPy==1.11.3",
    "radar-scenes==1.0.2",
    "scipy==1.5.4",
    "shiboken2==5.15.2",
    "six==1.16.0",
    "vispy==0.9.4",
    "trimesh==3.9.35"
]

tests_require = [

]

setuptools.setup(
    name="vispy_radar_scenes",
    version=verstr,
    author="Henrik Söderlund",
    author_email="henrik.a.soderlund@hotmail.com",
    maintainer="Henrik Söderlund",
    description="Fast visualization tool for RadarScenes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oleschum/radar_scenes",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    install_requires=install_requires,
    tests_require=tests_require,
package_data={'': ['*.png', '*.glsl', '*.stl', '*.obj']},
    keywords=["radar", "classification", "automotive", "machine learning"],
    entry_points={
        'gui_scripts': [
            'vispy_rad_viewer = vispy_radar_scenes.run:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
