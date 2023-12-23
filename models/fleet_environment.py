import sys
import sumolib
import networkx as nx
import matplotlib.pyplot as plt
import random

from models import demand
from models import dijkstra
from models import environment

def print_progress_bar(iteration, limit, prefix, suffix):
    fill='█'
    length = 50

    percent = ("{0:.1f}").format(100 * (iteration / float(limit)))
    filled_length = int(length * iteration // limit)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)

class traffic_env:
    def __init__ (self, network_file, congestion = [], evaluation = "", congestion_level = "", num_vehicle = 20, num_demands = 200):
        # 1. Define network_file
        self.network_file = network_file  # read the file

        self.net = sumolib.net.readNet(network_file)  # file -> net
        self.nodes = [node.getID().upper() for node in self.net.getNodes()]  # net -> nodes (ID)
        self.edges = [edge.getID() for edge in self.net.getEdges()]  # net -> edges (ID)
        self.state_space = self.nodes  # state_space

        # 2. Define congestions edges with its original pattern
        if congestion:  # if congestion is defined
            self.congested_edges = [item[0] for item in congestion]
            self.congestion_duration = [item[1] for item in congestion]  # the duration of so called "traffic jam"

            for edge in self.congested_edges:  # make sure that all congested_edges are in the net
                if edge not in self.edges:
                    sys.exit(f'Error: Invalid congestion_edges {edge}')
            # print(f'Congested Edges: {list(zip(self.congested_edges, self.congestion_duration))}')
            # print(f'Congested/Total: {len(self.congested_edges)}/{len(self.edges)}')

        else:  # if congestion is not defined, then set edges and its duration randomly
            if congestion_level == "low":
                traffic_level = 0.05  # 5% congested
            elif congestion_level == "medium":
                traffic_level = 0.10  # 10% congested
            elif congestion_level == "high":
                traffic_level = 0.20  # 20% congested
            self.congested_edges = random.sample(self.edges, round(len(self.edges) * traffic_level))
            self.congestion_duration = [random.randint(60, 120) for _ in range(len(self.congested_edges))]  # 1~2 min


        # 3. Define evaluation type
        if evaluation not in ('distance', 'time'):
            sys.exit('Error: Invalid evaluation type, provide only "distance" or "time"')
        self.evaluation = evaluation

        # 4. Distribute vehicles in different place
        self.num_vehicle = num_vehicle
        self.vehicle_states = []  # list[num_vehicle]
        self.timeline = []  # list[num_vehicle][current_time]
        self.current_time = 0
        self.reset()

        # 5. Define demands
        offset = 0
        self.num_demands = num_demands
        self.demands = demand.Demand(network_file, offset, num_demands = self.num_demands)
        self.demand_queue = []
        self.current_demand = 0




    # Initialise
    def reset (self):
        """
        Args:
        - void

        Returns:
        """

        self.vehicle_states = random.choices(self.state_space, k = self.num_vehicle)
        self.timeline = [[] for _ in range(self.num_vehicle)]
        print(f'-- Initial vehicle states: {self.vehicle_states}\n')


    #
    def get_congestion (self):
        """
        Returns:
            - congested_edges
        """
        return list(zip(self.congested_edges, self.congestion_duration))



    #
    def is_empty (self):
        """
        if demand_queue = [], then return True

        Returns:
        - True/False
        """
        return self.current_demand == self.num_demands and self.demand_queue == []



    #
    def update_demand_queue (self):
        """

        Args:
        - demand(departure_time, start_node, end_node)
        - timeline

        Returns:
        - demand_queue[-1]
        """
        # 1. Pull demand
        self.demand_queue.append(self.demands.push())
        self.current_demand += 1

        departure_time = self.demand_queue[-1][0]
        start_node = self.demand_queue[-1][1]
        end_node = self.demand_queue[-1][2]

        # 2. Update timeline
        for _ in range(departure_time - self.current_time):
            for vehicle in range(self.num_vehicle):
                if len(self.timeline[vehicle]) < departure_time:
                    self.timeline[vehicle].append(0)
            # print('timeline update')
            # for vehicle in range(self.num_vehicle):
            #     print(f'{self.timeline[vehicle]}')

        self.current_time = departure_time


        # 3. Pop queue
        self.demand_queue.pop(0)


        print(f"-- Demand {self.current_demand}: from '{start_node[0]}' to '{end_node[0]}' at time {departure_time}")
        return start_node[0], end_node[0]



    #
    def get_neerest_vehicle (self, start_node):
        """

        Returns:
        - v_id
        """
        v_id = -1

        distance_lst = {vehicle: float('inf') for vehicle in range(self.num_vehicle)}
        print(distance_lst)

        for vehicle in range(self.num_vehicle):
            # Check if the vehicle is working
            print_progress_bar(vehicle, self.num_vehicle-1, "Finding", "")
            if self.current_time < len(self.timeline[vehicle]):
                continue

            # if the vehicle is idle
            vehicle_node = self.vehicle_states[vehicle]

            mock_env = environment.traffic_env(network_file = self.network_file, tls = [], evaluation="distance")
            mock_agent = dijkstra.Dijkstra(mock_env, vehicle_node, start_node)  # not a agent actually
            _, edge_path = mock_agent.search()
            distance_lst[vehicle] = mock_env.get_edge_distance(edge_path)


        print(distance_lst)

        if min(distance_lst) < float('inf'):
            v_id = min(distance_lst, key=lambda k: distance_lst[k])


        print(f'\n-- Assigned vehicle id: {v_id}\n')
        return v_id



    #
    def set_vehicle_working (self, v_id, working_time):
        """

        Returns:
        - void
        """
        for _ in range(working_time):
            self.timeline[v_id].append(1)




    #
    def fill_timeline (self):
        """

        Args:
        - void

        Returns:
        - void
        """
        max_length = max(len(row) for row in self.timeline)
        self.timeline = [row + [0] * (max_length - len(row)) for row in self.timeline]



    # def set_plot_visualised_result (self, node_path, edge_path):
    #     """
    #
    #     Args:
    #     - node_path: [num_demands]
    #     - edge_path: [num_demands]
    #
    #     Returns:
    #     - Graph
    #     """



    #
    def plot_gantt (self):
        """

        """
        self.fill_timeline()
        plt.imshow(self.timeline, cmap='Greys', aspect='auto', interpolation='nearest')
        plt.xlabel('Time')
        plt.ylabel('Vehicle')
        plt.yticks(range(self.num_vehicle))
        plt.show()



    #
    def get_total_time (self):
        """

        """
        max_length = max(len(row) for row in self.timeline)
        return max_length
