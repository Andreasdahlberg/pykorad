#!/usr/bin/env python3
# -*- coding: utf-8 -*
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import serial

__author__ = 'andreas.dahlberg90@gmail.com (Andreas Dahlberg)'
__version__ = '0.1.0'

OUTPUT_ENABLED_MASK = 0x40
OVER_CURRENT_PROTECTION_ENABLED_MASK = 0x20
OVER_VOLTAGE_PROTECTION_ENABLED_MASK = 0x80
CC_CV_MASK = 0x01

class PowerSupply(object):
    """ A remote programmable power supply."""
    def __init__(self, port, baudrate=9600, timeout=0.05):
        self._serial_port = serial.Serial(port, baudrate, timeout=timeout)

        self._id = self._get_id()


    def __str__(self):
        return '<PowerSupply> {}'.format(self.get_identification())


    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        self._serial_port.close()


    def _execute_command(self, command, decode=True):
        self._serial_port.write(command)

        data = bytearray()

        # Read bytes until no more data is available.
        while True:
            byte = self._serial_port.read()
            if byte:
                data.extend(byte)
            else:
                break

        data = self._perform_bug_workarounds(command, data)

        if decode:
            return self._decode_response(data)
        else:
            return data


    def _perform_bug_workarounds(self, command, data):
        # The ISET1? command may return an extra byte on some devices.
        # Remove this extra byte as a workaround.
        if command == b'ISET1?' and len(data) == 6:
            data = data [:-1]

        return data


    def _decode_response(self, response):
        # Try to convert to float. If this fails, assume the response is a string.
        try:
            value = float(response)
        except ValueError:
            value = response.decode("utf-8")

        return value


    def set_output_voltage(self, voltage):
        """Set the maximum output voltage. (0.0 - 30.0) V"""

        # NOTE: The PS will accept voltages up to 31.0 V but is only rated for 30.0 V.
        assert voltage >= 0.0
        assert voltage <= 30.0

        command_str = 'VSET1:{}'.format(voltage)
        command = command_str.encode("utf-8")
        self._execute_command(command)


    def get_requested_output_voltage(self):
        """Get the requested output voltage. (0.0 - 31.0) V"""

        command = 'VSET1?'.encode("utf-8")
        return self._execute_command(command)


    def get_output_voltage(self):
        """Get the actual output voltage. (0.0 - 31.0) V"""

        command = 'VOUT1?'.encode("utf-8")
        return self._execute_command(command)

    def set_output_current(self, current):
        """Set the maximum output current. (0.0 - 5.0) A"""

        # NOTE: The PS will accept currents up to 5.1 A but is only rated for 5.0 A.
        assert current >= 0.0
        assert current <= 5.0

        command_str = 'ISET1:{}'.format(current)
        command = command_str.encode("utf-8")
        self._execute_command(command)


    def get_output_current(self):
        """Get the actual output current. (0.0 - 5.1) A"""

        command = 'IOUT1?'.encode("utf-8")
        return self._execute_command(command)


    def get_requested_output_current(self):
        """Get the requested output current. (0.0 - 5.1) V"""

        command = 'ISET1?'.encode("utf-8")
        return self._execute_command(command)


    def recall_from_memory(self, index):
        """Recalls voltage and current limits from memory. (1 - 5)"""

        assert index >= 1
        assert index <= 5

        command_str = 'RCL{}'.format(index)
        command = command_str.encode("utf-8")
        self._execute_command(command)


    def save_to_memory(self, index):
        """Saves voltage and current limits to memory. (1 - 5)"""

        assert index >= 1
        assert index <= 5

        command_str = 'SAV{}'.format(index)
        command = command_str.encode("utf-8")
        self._execute_command(command)


    def enable_output(self, enable):
        """Enable/Disable the power output."""
        if enable:
            command_str = 'OUT1'
        else:
            command_str = 'OUT0'

        command = command_str.encode("utf-8")
        self._execute_command(command)


    def enable_over_voltage_protection(self, enable):
        """Enable/Disable the over voltage protection.The PS will switch off
           the output when the voltage rises above the requested voltage."""

        if enable:
            command_str = 'OVP1'
        else:
            command_str = 'OVP0'

        command = command_str.encode("utf-8")
        self._execute_command(command)


    def enable_over_current_protection(self, enable):
        """Enable/Disable the over current protection.The PS will switch off
           the output when the current rises above the requested current."""

        if enable:
            command_str = 'OCP1'
        else:
            command_str = 'OCP0'

        command = command_str.encode("utf-8")
        self._execute_command(command)


    def _get_id(self):
        command = '*IDN?'.encode("utf-8")
        return self._execute_command(command)


    def get_identification(self):
        """Get the device identification string."""

        return self._id

    def is_output_enabled(self):
        """Check if the power output is enabled."""

        command = 'STATUS?'.encode("utf-8")
        return bool(self._execute_command(command, False)[0] & OUTPUT_ENABLED_MASK)


    def is_over_voltage_protection_enabled(self):
        """Check if over voltage protection is enabled."""
        return self._is_protection_enabled(OVER_VOLTAGE_PROTECTION_ENABLED_MASK)


    def is_over_current_protection_enabled(self):
        """Check if over current protection is enabled."""
        return self._is_protection_enabled(OVER_CURRENT_PROTECTION_ENABLED_MASK)


    def _is_protection_enabled(self, mask):
        command = 'STATUS?'.encode("utf-8")

        counter = 0
        while counter < 3:
            data = self._execute_command(command, False)
            if len(data) == 1:
                return bool(data[0] & mask)

            counter = counter + 1
        return False
