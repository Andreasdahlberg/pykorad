"""This example shows how to use the pykorad module by implementing a basic CLI interface."""

import sys
import argparse

sys.path.append('../')
from pykorad import PowerSupply

def main():
    """Parse arguments and configure the power supply."""
    parser = argparse.ArgumentParser()

    parser.add_argument('port', help='Serial port to use, ex. /dev/ttyACMx.')

    parser.add_argument('-i', '--identification', help=PowerSupply.get_identification.__doc__,
                        action='store_true')

    parser.add_argument('-c', '--current', type=float, help=PowerSupply.set_output_current.__doc__)
    parser.add_argument('-v', '--voltage', type=float, help=PowerSupply.set_output_voltage.__doc__)

    parser.add_argument('-m', '--memory', type=int, help=PowerSupply.recall_from_memory.__doc__)

    parser.add_argument('-C', '--currentout', help=PowerSupply.get_output_current.__doc__,
                        action='store_true')
    parser.add_argument('-V', '--voltageout', help=PowerSupply.get_output_voltage.__doc__,
                        action='store_true')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-e', '--enable', dest='enable', help='Enable the power supply output',
                       default=None, action='store_true')
    group.add_argument('-d', '--disable', dest='enable', help='Disable the power supply output',
                       default=None, action='store_false')

    args = parser.parse_args()

    power_suppy = PowerSupply(args.port)

    if args.identification:
        print(power_suppy.get_identification())

    if args.current != None:
        power_suppy.set_output_current(args.current)

    if args.voltage != None:
        power_suppy.set_output_voltage(args.voltage)

    if args.memory != None:
        power_suppy.recall_from_memory(args.memory)

    if args.voltageout:
        print("Voltage: {} V".format(power_suppy.get_output_voltage()))

    if args.currentout:
        print("Current: {} A".format(power_suppy.get_output_current()))

    if args.enable != None:
        power_suppy.enable_output(args.enable)

    return 0


if __name__ == '__main__':
    exit(main())