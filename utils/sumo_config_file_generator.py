import argparse

import glob
import os
import sys
import lxml.etree as ET
import tempfile


# carla library
try:
    sys.path.append(glob.glob('../carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# sumo library
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import sumolib 
from sumo_integration.carla_simulation import CarlaSimulation

from util.netconvert_carla import netconvert_carla



def write_sumocfg_xml(cfg_file, net_file, vtypes_file, viewsettings_file, additional_traci_clients=0):
    """
    Writes sumo configuration xml file.
    """
    root = ET.Element('configuration')

    input_tag = ET.SubElement(root, 'input')
    ET.SubElement(input_tag, 'net-file', {'value': net_file})
    ET.SubElement(input_tag, 'route-files', {'value': vtypes_file})

    gui_tag = ET.SubElement(root, 'gui_only')
    ET.SubElement(gui_tag, 'gui-settings-file', {'value': viewsettings_file})

    ET.SubElement(root, 'num-clients', {'value': str(additional_traci_clients+1)})

    tree = ET.ElementTree(root)
    tree.write(cfg_file, pretty_print=True, encoding='UTF-8', xml_declaration=True)



def main(args):

	# Temporal folder to save intermediate files.
    tmpdir = tempfile.mkdtemp()
    basedir = os.path.dirname(os.path.realpath(__file__))

    # carla simulation
    carla_simulation = CarlaSimulation(args.host, args.port, args.step_length)
    world = carla_simulation.client.get_world()
    current_map = world.get_map()

    xodr_file = os.path.join(tmpdir, current_map.name + '.xodr')
    current_map.save_to_disk(xodr_file)


    # sumo simulation
    net_file = os.path.join(basedir, 'sumo_config', current_map.name + '.net.xml')
    netconvert_carla(xodr_file, net_file, guess_tls=True)

    cfg_file = os.path.join(basedir, 'sumo_config', current_map.name + '.sumocfg')
    vtypes_file = os.path.join(basedir, 'sumo_config', 'carlavtypes.rou.xml')
    viewsettings_file = os.path.join(basedir, 'sumo_config', 'viewsettings.xml')


    write_sumocfg_xml(cfg_file, net_file, vtypes_file, viewsettings_file)

    sumo_net = sumolib.net.readNet(net_file)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('--host',
                           metavar='H',
                           default='127.0.0.1',
                           help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument('-p',
                           '--port',
                           metavar='P',
                           default=2000,
                           type=int,
                           help='TCP port to listen to (default: 2000)')
    argparser.add_argument('--step-length',
                           default=0.1,
                           type=float,
                           help='set fixed delta seconds (default: 0.1s)')

    args = argparser.parse_args()

    main(args)