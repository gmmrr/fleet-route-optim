import sumolib
import random

from models import environment
from models import dijkstra

class Demand:
    def __init__(self, network_file, tls, offset=0, num_demands=200):
        self.network_file = network_file

        self.net = sumolib.net.readNet(network_file)  # file -> net
        self.nodes = [node.getID().upper() for node in self.net.getNodes()]  # net -> nodes (ID)
        self.edges = [edge.getID() for edge in self.net.getEdges()]  # net -> edges (ID)
        self.state_space = self.nodes  # state_space

        self.tls = tls

        self.offset = offset  # this is a reserved term for future use with a known dataset
        self.num_demands = num_demands
        self.current_time = 0
        self.current_demand = 0



    def push (self):
        """
        Push a demand to the environment
        Note that at this moment, demands are randomly generated

        Returns:
        - asking_time (int)
        - start_node (str)
        - end_node (str)
        """
        # Make sure the travel time is not too short, it is necessary to be close to reality
        travel_time = 0
        while travel_time < 100:    # 100 seconds stands for 1.67 minutes
            # Randomly generate a demand
            asking_time = self.current_time + random.randint(10, 30)
            start_node = random.choices(self.state_space)
            end_node = random.choices(self.state_space)
            while end_node == start_node:
                end_node = random.choices(self.state_space)

            # Get the travel time
            mock_env = environment.traffic_env(network_file = self.network_file, tls = self.tls, evaluation="time")
            mock_agent = dijkstra.Dijkstra(mock_env, start_node[0], end_node[0])  # not a agent actually
            _, edge_path = mock_agent.search()
            travel_time = mock_env.get_edge_time(edge_path)

        # Update the current time and demand
        self.current_time = asking_time
        self.current_demand += 1

        return [asking_time, start_node, end_node]
