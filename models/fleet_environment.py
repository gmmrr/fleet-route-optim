import sys
import sumolib
import networkx as nx
import matplotlib.pyplot as plt
import random
import math

from models import demand
from models import dijkstra
from models import environment
from utilities import progressbar


class traffic_env:
    def __init__ (self, network_file, tls, evaluation = "", congestion = [], congestion_level = "", num_vehicle = 20, num_demands = 200):
        # 01 Define network_file
        self.network_file = network_file  # read the file

        self.net = sumolib.net.readNet(network_file)  # file -> net
        self.nodes = [node.getID().upper() for node in self.net.getNodes()]  # net -> nodes (ID)
        self.edges = [edge.getID() for edge in self.net.getEdges()]  # net -> edges (ID)
        self.state_space = self.nodes  # state_space

        self.tls = tls


        # 02 Define evaluation type
        if evaluation not in ('distance', 'time'):
            sys.exit('Error: Invalid evaluation type, provide only "distance" or "time"')
        self.evaluation = evaluation


        # 03 Define congestions edges with its original pattern
        if congestion:  # if congestion is defined
            self.congested_edges = [item[0] for item in congestion]
            self.congestion_duration = [item[1] for item in congestion]  # the duration of so called "traffic jam"

            for edge in self.congested_edges:  # make sure that all congested_edges are in the net
                if edge not in self.edges:
                    sys.exit(f'Error: Invalid congestion_edges {edge}')

        else:  # if congestion is not defined, then set edges and its duration randomly
            if congestion_level == "low":
                traffic_level = 0.05  # 5% congested
            elif congestion_level == "medium":
                traffic_level = 0.10  # 10% congested
            elif congestion_level == "high":
                traffic_level = 0.20  # 20% congested
            self.congested_edges = random.sample(self.edges, round(len(self.edges) * traffic_level))
            self.congestion_duration = [random.randint(60, 120) for _ in range(len(self.congested_edges))]  # 1~2 min



        # 04 Distribute vehicles in different place and reset their props
        self.num_vehicle = num_vehicle
        self.vehicle_states = []  # list[num_vehicle]
        self.timeline = []  # list[num_vehicle][current_time]
        self.asking_time = 0  # record the time demand give to us
        self.waiting_counter = 0  # add busy_time and commute_time, i.e. summing up the time that every passenger is going to wait
        self.reset()  # reset vehicle_states and timeline

        # 05 Define demands
        offset = 0
        self.num_demands = num_demands
        self.demands = demand.Demand(network_file, tls, offset, num_demands = self.num_demands)
        self.demand_queue = []  # record demands
        self.demands_counter = 0


        # 05 Print props of the network
        print(f'Congested Edges: {list(zip(self.congested_edges, self.congestion_duration))}')
        print(f'Congested/Total: {len(self.congested_edges)}/{len(self.edges)}\n')


    # ----- Initialisation

    def reset (self):
        """
        Initialise vehicle_states randomly and set timeline to 0 (in first column)

        Args:
        - vehicle_states[num_vehicles]
        - timeline[num_vehicles][seconds]
        """
        self.vehicle_states = random.choices(self.state_space, k = self.num_vehicle)
        self.timeline = [[] for _ in range(self.num_vehicle)]
        print(f'-- Initial vehicle states: {self.vehicle_states}\n')



    def get_congestion (self):
        """
        Return the congestion edges and its duration for others to use in individual env

        Returns:
        - congestion (list[tuple(edge_id, int(minute))])
        """
        return list(zip(self.congested_edges, self.congestion_duration))



    # ----- Main function (following four functions form a pipeline executing "once" in every demand)

    #
    def update_demand_queue (self):
        """
        Get the next demand and pop the oldest one to run

        Args:
        - demand(departure_time, start_node, end_node)
        - demand_queue
        - asking_time

        Returns:
        - start_node (str): actually ID
        - end_node (str)
        """
        # 01 Pull demand
        self.demand_queue.append(self.demands.push())
        self.demands_counter += 1

        self.asking_time = self.demand_queue[-1][0]
        start_node = self.demand_queue[-1][1]
        end_node = self.demand_queue[-1][2]


        print(f"-- Demand {self.demands_counter}: from '{start_node[0]}' to '{end_node[0]}")


        # 02 Pop demand
        self.demand_queue.pop()


        return start_node[0], end_node[0]



    #
    def get_neerest_vehicle (self, start_node):
        """
        Get the nearest vehicle and the time it takes to go to the next demand

        Returns:
        - v_id
        - commute_time: time that v_id taken to go to the next demand
        """

        # 01 Define "time_lst" to record the time it spend for the current state to the target point
        time_lst = {vehicle: float('inf') for vehicle in range(self.num_vehicle)}  # initialise to [inf, inf, inf, ...]

        for vehicle in range(self.num_vehicle):
            # Check if the vehicle is working
            finding_bar = progressbar.ProgressBar(vehicle, self.num_vehicle-1, "Finding", "")
            finding_bar.print()

            if self.asking_time < len(self.timeline[vehicle]):
                continue

            # Check if the vehicle is idle
            mock_env = environment.traffic_env(network_file = self.network_file, tls = self.tls, evaluation="time")
            mock_agent = dijkstra.Dijkstra(mock_env, self.vehicle_states[vehicle], start_node)  # not a agent actually
            _, edge_path = mock_agent.search()

            time_lst[vehicle] = mock_env.get_edge_time(edge_path)  # set to [XXX, XXX, inf, ...]. If inf ocuurs, corresponding vehicles are busy


        # 02 Use "time_lst" to distinguish which case the env is
        # Case 1: All the vehicles are busy
        if all(math.isinf(value) for value in time_lst.values()):

            # .01 Get which vehicle and when is it going to be available
            available_time, v_id = min((len(row), index) for index, row in enumerate(self.timeline))

            # .02 Get the time it spends from idle to the next demand point
            mock_env = environment.traffic_env(network_file = self.network_file, tls = self.tls, evaluation="time")
            mock_agent = dijkstra.Dijkstra(mock_env, self.vehicle_states[v_id], start_node)  # not a agent actually
            _, edge_path = mock_agent.search()
            commute_time = math.ceil(mock_env.get_edge_time(edge_path))

            # .03 Set it to the busy time
            busy_time = available_time - self.asking_time
            self.waiting_counter += busy_time + commute_time

            print(f'-- All vehicles are busy. After waiting, assigned vehicle id: {v_id}')

        # Case 2: Some vehicles are available
        else:

            # .01 Get which vehicle and when is it going to be available
            v_id = min(time_lst, key=lambda k: time_lst[k])

            # .02 Get the time it spends from idle to the next demand point
            mock_env = environment.traffic_env(network_file = self.network_file, tls = self.tls, evaluation="time")
            mock_agent = dijkstra.Dijkstra(mock_env, self.vehicle_states[v_id], start_node)  # not a agent actually
            _, edge_path = mock_agent.search()
            commute_time = math.ceil(mock_env.get_edge_time(edge_path))

            # .03 Set it to the busy time
            busy_time = 0
            self.waiting_counter += commute_time

            print(f'\n-- Assigned vehicle id: {v_id}')



        # 03 Update idle timeline
        self.update_idle_timeline()


        print(f"-- Departure time {self.asking_time + busy_time + commute_time} (asking time: {self.asking_time} + commuting time: {commute_time})\n")


        return v_id, commute_time




    def update_idle_timeline (self):
        """
        Insert 0 to the idle timeline until the asking_time

        Args:
        - timeline[num_vehicle][seconds]
        """
        for vehicle in range(self.num_vehicle):
            while len(self.timeline[vehicle]) < self.asking_time:
                self.timeline[vehicle].append(0)




    #
    def set_vehicle_working (self, v_id, commute_time, working_time, end_node):
        """
        Insert 0.5 to the timeline for commute_time and 1 for working_time

        Args:
        - timeline[num_vehicle][seconds]
        """
        for _ in range(commute_time):
            self.timeline[v_id].append(0.5)

        for _ in range(working_time):
            self.timeline[v_id].append(1)

        self.vehicle_states[v_id] = end_node





    # ----- print result


    #
    def fill_timeline (self):
        """
        Fill the timeline with 0 to make it a rectangle

        Args:
        - timeline[num_vehicle][seconds]
        """
        max_length = max(len(row) for row in self.timeline)
        self.timeline = [row + [0] * (max_length - len(row)) for row in self.timeline]



    # print result
    def print_result (self):
        """
        Print the result of the simulation
        """
        max_length = max(len(row) for row in self.timeline)

        print(f'-- Total Time: {round(max_length/60, 2)} min')
        print(f'-- Average Waiting Time: {round(self.waiting_counter/self.num_demands/60, 2)} min')


    #
    def plot_gantt (self):
        """
        Plot the gantt chart of the simulation
        """
        self.fill_timeline()
        plt.imshow(self.timeline, cmap='Greys', aspect='auto', interpolation='nearest')
        plt.xlabel('Time')
        plt.ylabel('Vehicle')
        plt.yticks(range(self.num_vehicle))
        plt.show()


    #
    def plot_visualised_result (self, node_path, edge_path):
        """

        """

        nodes_dict = {}  # a list of x_coord and y_coord of every nodes
        for node in self.nodes:
            x_coord, y_coord = self.net.getNode(node).getCoord()
            nodes_dict[node] = (x_coord, y_coord)

        edges_dict = {}  # a list of from_point and to_point of every edges
        for edge in self.edges:
            from_id = self.net.getEdge(edge).getFromNode().getID()
            to_id = self.net.getEdge(edge).getToNode().getID()
            edges_dict[edge] = (from_id, to_id)

        # Draw the network layout
        net_G = nx.Graph()
        for edge in edges_dict:
            net_G.add_edge(edges_dict[edge][0], edges_dict[edge][1])
        pos = {node: nodes_dict[node] for node in nodes_dict}
        nx.draw(
            net_G, pos, with_labels=False,
            node_color='DimGray', node_size=10,
            edge_color='DarkGray'
        )

        # Draw the selected route
        for i in range(len(edge_path)):
            route_G = nx.Graph()
            for edge in edge_path[i]:
                route_G.add_edge(edges_dict[edge][0], edges_dict[edge][1])
            nx.draw(
                route_G, pos, with_labels=False,
                node_color=f'C{i}', node_size=30,
                edge_color=f'C{i}', width=3,
                arrows=True, arrowsize=7, arrowstyle='-|>'
            )

        # Draw traffic light nodes and congested edges in time evaluation
        if self.evaluation in ("time"):
            congested_lst = [edges_dict[edge] for edge in self.congested_edges]  # congested edges
            nx.draw_networkx_edges(
                net_G, pos,
                edgelist=congested_lst, edge_color='Gold', width=3
            )

        plt.show()
