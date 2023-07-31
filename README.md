# Privacy-preserving Traffic Flow Release with Consistency Constraints

This is the source code of paper "Privacy-preserving Traffic Flow Release with Consistency Constraints". Python and SUMO are used in this project.

## Install

Install SUMO from:
```
https://sumo.dlr.de/docs/TraCI.html
```

Download nerwork and route file into folder Datasets from :
```
Bologna: http://www.cs.unibo.it/projects/bolognaringway/

Berlin: https://github.com/mosaic-addons/best-scenario
```
## Usage

### Global DP
1. Experiment parameters setting:

EPSILON: Privacy budget.

START_TIME: Statistics of the start time points of trajectories.

NET_NAME: Name of network, 'bolognaringway' and 'pasubio' are available in our experiments.

TIMESTEP: Timeslot of experiment.

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
2. Export the trajectory data from SUMO:

```
python3 local DP/Trajectory_Generation.py
```
3. Get the experiment result:

```
python3 local DP/optRR.py
```
