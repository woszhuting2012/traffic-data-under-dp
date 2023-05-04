# Privacy-preserving Traffic Flow Release with Consistency Constraints

This is the source code of paper "Privacy-preserving Traffic Flow Release with Consistency Constraints". Python and SUMO are used in this project.

## Install

Install SUMO from:
```
https://sumo.dlr.de/docs/TraCI.html
```

Download nerwork and route file from :
```
Bologna: http://www.cs.unibo.it/projects/bolognaringway/

Pasubio: https://github.com/DLR-TS/sumo-scenarios/tree/main/bologna/](https://github.com/DLR-TS/sumo-scenarios/tree/main/bologna/pasubio
```
## Usage

### Local DP
1. Experiment parameters setting in init.py
EPSILON: Privacy budget.
START_TIME, END_TIME: Statistics of the start and end time points of vehicles.
block_x, block_y, UNIT_LEN: The position and size of district.
NET_NAME: Name of network, 'bolognaringway' and 'pasubio' are available in our experiments.
TIMESTEP: Timeslot of experiment. We set it to 450s in experiments.
MAX_TRA: Maximum trajectory length.

Make parameters effective:
```
python3 init.py
```

2. Export the trajectory data from SUMO:

```
python3 Trajectory_Generation.py
```

3. Add the noisy to data:

```
python3 Noise_Addition.py
```
