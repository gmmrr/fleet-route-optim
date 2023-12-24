# fleet-route-optim
<img width="773" alt="Screenshot 2023-12-24 at 21 58 29" src="https://github.com/gmmrr/fleet-route-optim/assets/88712124/7364049a-68f3-47a9-9fa6-428fd3f912ea">

## Description
This project aims to solve the route optimisation problem among vehicles in a fleet by reinforcement learning.<br>

Giving a group of vehicles and a serial of demands, it can assign a particular vehicle to deal with it intuitively, and each of them will follow the route computed by RL.<br>

The performance of RL for each episodes executed in this project can be found in <a href="https://github.com/gmmrr/route-optim">gmmrr/route-optim<a/>, which is an individual version of this repo.<br>

This repo is part of Guanming's capstone project.

## Result
Given that there are 20 vehicles, and 200 demands are randomly generated with 10 ~ 30 seconds intervals.<br>

The visualised result is in the plot below:<br>
<img width="590" alt="Screenshot 2023-12-24 at 21 21 49" src="https://github.com/gmmrr/fleet-route-optim/assets/88712124/ecc84a08-9ff7-4a5d-8e0d-5167c2b19945"><br>
where the grey part showcases the duration that the vehicle is commuting, and the black part showcases the duration that the vehicle is on duty.<br>

These demands are consumed as below:<br>
```
-- Total Time: 69.58 min
-- Average Waiting Time: 0.58 min
```

The graph below the topic section roughly shows 10 of demands and how vehicles find their route, where yellow lines are congested edges.<br>

The graph below is the complete one:
<img width="891" alt="Screenshot 2023-12-24 at 22 44 22" src="https://github.com/gmmrr/fleet-route-optim/assets/88712124/dd1421ee-df40-4880-8ee8-1b69051a2f33">


## Project Scope
1. **Demands are randomly generated**<br>
    The prediction of next demand is quite a issue, but it is really hard to get the real situation near NCKU. There is a dataset called ```Cabspotting``` (a cab data revealed by Scott Snibbe from San Francisco) on which lots of related researches is based.
    
2. **Congestion is randomly generated**<br>
    Similar to mentioned situation above. It is randomly chosen from edges space, and it can be defined in ```fleet_environment.py``` to low, medium, or high level.

3. **Speed is a constant**<br>
    Net downloaded from OSM website helps classify the edge type, like primary, secondary, residential highway. Each of them has a defined speed. In this project, we don't take acceleration into consideration. Thus, it seems like to be far away from the practical case.

4. **Traffic light is set in a 90 seconds interval**<br>
    Even if it is close to the practical case, it is still not real. They are set as a program rather than a constant pattern in reality.

5. **The terminal condition of RL**<br>
    It is set that convergence occurs when time taken (round to the second decimal place) in 5 episodes is consistent.

6. **Performance issue**<br>
    Due to the performance issue, part of simulation is implemented by Dijkstra algorithm. Even if so, the most important part, that is, route optimisation is still implemented by RL.

## Setup
1. Download SUMO (https://sumo.dlr.de/docs/Downloads.php)
2. Clone this repository to your local machine
3. Install the necessary packages by following operations:
```python
$ pip3 install -r requirements.txt
```
4. Update the main.py with your SUMO directory to set the environment variable
```python
def sumo_config():
    os.environ["SUMO_HOME"] = '$SUMO_HOME' # -- change to your path to $SUMO_HOME
    ...
```
5. Upload your netedit file and update the network_file variable
```python
network_file = './network_files/ncku_network.net.xml'
```
More on **OSM website**: https://www.openstreetmap.org/ <br>
Config command is saved in ```./network_files/config.txt```

6. Upload your traffic_light file
```python
tls = tls_from_tllxml('./network_files/ncku_network.tll.xml')
```
This file can be converted by **Netedit**, more on https://sumo.dlr.de/docs/Netedit/index.html

7. Edit following parameters as part of environment in ```main.py```
```python
# 03 Initiate Environment
...
num_vehicle = 20
evaluation = "time"
num_demands = 200
congestion_assigned = []  # Type: ["edge_id", int(minute)] It will be defined randomly if not customised
...
```
8. Run the code
```terminal
$ python3 main.py
```

## Customisable Section
1. In ```main.py```, we can set
   ```python
    num_vehicle = 20
    evaluation = "time"
    num_demands = 200
    congestion_assigned = []
   ```
2. In ```agent.py```, we can set
   ```python
    # Hyperparameters for Q_Learning
    learning_rate = 0.9  # alpha
    discount_factor = 0.1  # gamma

    # Hyperparameters for SARSA
    learning_rate = 0.9  # alpha
    discount_factor = 0.1  # gamma
    exploration_rate = 0.1  # ratio of exploration and exploitation
   ```
   and we have
   ```python
    reward_lst = [-50, -50, -30, 100, 50, -1]
   ```
   They are defined as ```[invalid_action_reward, dead_end_reward, loop_reward, completion_reward, bonus_reward, continue_reward]``` respectively.


