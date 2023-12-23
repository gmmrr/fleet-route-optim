import sys
import sumolib
import math
import networkx as nx
import matplotlib.pyplot as plt
import random

class Demand:
    def __init__(self, network_file, offset=0, num_demands=200):
        self.network_file = network_file

        self.net = sumolib.net.readNet(network_file)  # file -> net
        self.nodes = [node.getID().upper() for node in self.net.getNodes()]  # net -> nodes (ID)
        self.edges = [edge.getID() for edge in self.net.getEdges()]  # net -> edges (ID)
        self.state_space = self.nodes  # state_space

        self.offset = offset
        self.num_demands = num_demands
        self.current_time = 0
        self.current_demand = 0



    def push (self):
        """
        Args:
        -

        Returns:
        -
        """
        departure_time = self.current_time + random.randint(1, 5)
        start_node = random.choices(self.state_space)
        end_node = random.choices(self.state_space)
        while end_node == start_node:
            end_node = random.choices(self.state_space)

        self.current_time = departure_time
        self.current_demand += 1

        return [departure_time, start_node, end_node]
