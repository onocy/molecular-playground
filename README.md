# Molecular Playground 

Local Python Server

- Adapted from Victor Dibia, Real-time Hand-Detection using Neural Networks (SSD) on Tensorflow, (2017), GitHub repository, https://github.com/victordibia/handtracking

### To Run

> Make sure that you have python >3.6 installed ([install here], as well as Java.(https://www.python.org/downloads/))

1. Clone the repository

`git clone <url>`

2. Run the detection script (Note: this should take several seconds, as the NN graph is loaded and the workers begin)

`python detect_mult_threaded.py`

1. Run the local JMOL molecule.

`java -jar MPJmolApp.jar`

---
![motion](assets/motion.gif)

### Script Options

* `-src` : video source, default = 0
* `-nhands` : number of hands, default = 2
* `-fps` : show frames per second: default = 1 [yes]
* `-display` : show output for display: default = 1 [yes]
* `-num-w` : number of workers for processing: default = 4
* `-flip-x-axis`: flip x axis if camera facing installation: default = 0 [no]
* `-flip-y-axis`: flip y axis if camera facing installation: default = 0 [no]

> example: python detect_multi_threaded.py -nhands 1 -fps 1 -ds 1 -num-w 5
