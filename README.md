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

### Global DP
1. Experiment parameters setting:

EPSILON: Privacy budget.

START_TIME, END_TIME: Statistics of the start and end time points of vehicles.

block_x, block_y, UNIT_LEN: The position and size of district.

NET_NAME: Name of network, 'bolognaringway' and 'pasubio' are available in our experiments.

TIMESTEP: Timeslot of experiment. We set it to 450s in experiments.

MAX_TRA: Maximum trajectory length.

Make parameters effective:
```
python3 global DP/init.py
```

2. Export the trajectory data from SUMO:

```
python3 global DP/Trajectory_Generation.py
```

3. Add the noisy to data:

```
python3 global DP/Noise_Addition.py
```

4. Generate the matrix and get experiment result:
```
pyhton3 global DP/Matrix_Result_Geeneration.py
```

### Local DP
1.Experiment parameters setting:

Set the same parameters as Global DP

```
python3 local DP/init.py
```

2. Get the experiment result:

```
python3 local DP/optRR.py
```
