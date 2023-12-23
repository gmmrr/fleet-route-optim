import os, sys
import xml.etree.ElementTree as ET
import math

from models import environment
from models import agent
from models import fleet_environment
from models import dijkstra

def sumo_config():
    # os.environ["SUMO_HOME"] = '$SUMO_HOME' # -- change to your path to $SUMO_HOME if necessary

    # Check if SUMO sucessfully configured
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")


def tls_from_tllxml(file_name):
    """
    Make tls data from tll.xml

    Args:
    - file_name: tll.xml file name
        <additionals>
            <tlLogic id="10726190730" type="static" programID="0" offset="0">
                <phase duration="42" state="GGgrrrGGgrrr"/>
                <phase duration="3"  state="yyyrrryyyrrr"/>
                <phase duration="42" state="rrrGGgrrrGGg"/>
                <phase duration="3"  state="rrryyyrrryyy"/>
            </tlLogic>
            <tlLogic id="" type="" programID="" offset="">
                <phase/>
            </tlLogic>
            ...
        </additionals>

    Returns:
    - tls_data: dictionary of tls data
        tls_data[tl_id][link_index] = [90]
    """
    tree = ET.parse(file_name)
    root = tree.getroot()

    tls_data = {}
    for tl in root.findall('.//tlLogic'):
        tl_id = tl.get('id')

        if tl_id not in tls_data:
            tls_data[tl_id] = {}
        else:
            sys.exit(f"Error: {tl_id} duplicated")

        phases = tl.findall('.//phase')

        for phase in phases:
            duration = phase.get('duration')
            state = phase.get('state')

            # Make tls_data[tl_id][link_index] = nth char in state repeating duration times
            for link_index in range(len(state)):
                if link_index not in tls_data[tl_id]:
                    tls_data[tl_id][link_index] = []
                tls_data[tl_id][link_index] += [state[link_index] for _ in range(int(duration))]

    return tls_data


if __name__ == '__main__':

    # 01 Setup SUMO
    sumo_config()


    # 02 Configure network variables
    network_file = './network_files/ncku_network.net.xml'
    tls = tls_from_tllxml('./network_files/ncku_network.tll.xml')
    congestion_assigned = []  # can be defined, but if it is empty, env will randomly decide congested edges

    # 03 Initiate Environment
    # ---------------------------
    # Edit
    # ---------------------------
    num_vehicle = 3
    evaluation = "time"
    num_demands = 10
    # ---------------------------
    #
    # ---------------------------

    fleet_env = fleet_environment.traffic_env(
        network_file = network_file,
        congestion = congestion_assigned,
        evaluation = evaluation,
        congestion_level = "low",
        num_vehicle = num_vehicle,
        num_demands = num_demands,
    )

    congestion = congestion_assigned if congestion_assigned else fleet_env.get_congestion()

    env = environment.traffic_env(
        network_file = network_file,
        tls = tls,
        congestion = congestion,
        evaluation = evaluation,
    )



    # demand_node_path = []  # [num_demands]
    # demand_edge_path = []  # [num_demands]

    # 04 Activate agents
    while not fleet_env.is_empty():
        # get the next demand
        start_node, end_node = fleet_env.update_demand_queue()
        if start_node == [] or end_node == []:
            print(f'Demand queue is empty now')
            continue

        # decide who to work
        v_id = fleet_env.get_neerest_vehicle(start_node)
        # if all vehicle working
        if v_id == -1:
            continue

        # QLearning_agent = agent.Q_Learning(env, start_node, end_node)
        # _, edge_path, _, _ = QLearning_agent.train(5000, 5)  # limit of episodes, threshold to converge

        Dijkstra = dijkstra.Dijkstra(env, start_node, end_node)
        _, edge_path = Dijkstra.search()


        working_time = math.ceil(env.get_edge_time(edge_path))
        fleet_env.set_vehicle_working(v_id, working_time)

        # demand_node_path.append(node_path)
        # demand_edge_path.append(edge_path)

    print(f'\n-- Total time: {round(fleet_env.get_total_time()/60, 2)} min')
    fleet_env.plot_gantt()
    # fleet_env.plot_visualised_result(demand_node_path, demand_edge_path)
