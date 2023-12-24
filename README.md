# fleet-route-optim

## Description
This project aims to solve the route optimisation problem among vehicles in a fleet by reinforcement learning.<br>

Giving a group of vehicles and a serial of demands, it can assign a particular vehicle to deal with it intuitively, and each of them will follow the route computed by RL.<br>

The performance of RL for each episodes executed in this project can be found in github.com/gmmrr/route-optim, which is an individual version of this repo.<br>

This repo is part of Guanming's capstone project.

## Result



## Project Scope
1. **Demands are randomly generated**<br>
    The prediction of next demand is quite a issue, but it is really hard to get the real situation near NCKU. There is a dataset called ```Cabspotting```(a cab data revealed by Scott Snibbe from San Francisco) on which lots of related researches is based.
    
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
    exploration_rate = 0.05  # ratio of exploration and exploitation
   ```
   and we have
   ```python
    reward_lst = [-100, -100, -100, 10, 100, -1]
   ```
   They are defined as below respectively.
   * invalid_action_reward
   * dead_end_reward 
   * loop_reward 
   * completion_reward  
   * bonus_reward  
   * continue_reward


