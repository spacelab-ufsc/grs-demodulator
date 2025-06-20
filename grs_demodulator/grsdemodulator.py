#
#  grsdemodulator.py
#  
#  Copyright The GRS Demodulator contributors.
#  
#  This file is part of GRS Demodulator.
#
#  GRS Demodulator is free software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  GRS Demodulator is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public
#  License along with GRS Demodulator; if not, see <http://www.gnu.org/licenses/>.
#  
#

import zmq

from gmsk import GMSK

class GRSDemodulator:
    """
    TODO
    """
    def __init__(self):
        """
        """

    def init_zmq(self):
        """
        """
        # Prepare ZMQ context and socket
        self._zmq_ctx = zmq.Context()

        # Create SUB socket
        self._in_socket = self._zmq_ctx.socket(zmq.SUB)

        # Create PUB socket
        self._out_socket = self._zmq_ctx.socket(zmq.PUB)

        # Bind to an address (SUB sockets will connect to this)
        self._out_socket.bind("tcp://*:5555")   # Bind to all interfaces on port 5555

    def run(self):
        """
        :return: None.
        """
        # Connect to the publisher (replace with your publisher's address)
        self._in_socket.connect("tcp://localhost:5555")

        # Subscribe to all messages (empty string) or specific topics
        self._in_socket.setsockopt_string(zmq.SUBSCRIBE, "") # Subscribe to all messages

        try:
            while True:
                # Receive message
                message = self._in_socket.recv_string()
                print(f"Received message: {message}")

        except KeyboardInterrupt:
            print("Subscriber interrupted")
        finally:
            # Clean up
            self._in_socket.close()
            self._zmq_ctx.term()
