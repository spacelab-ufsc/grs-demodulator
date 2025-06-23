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

import struct

import numpy as np
import zmq

from gmsk import GMSK

class GRSDemodulator:
    """
    Demodulator application.
    """
    def __init__(self):
        """
        Class constructor.

        :return: None.
        """

    def _init_zmq(self):
        """
        :return: None.
        """
        # Prepare ZMQ context and socket
        self._zmq_ctx = zmq.Context()

        # Create SUB socket
        self._in_socket = self._zmq_ctx.socket(zmq.SUB)

        # Optimizations
        self._in_socket.setsockopt(zmq.RCVHWM, 1000000) # High water mark
        self._in_socket.setsockopt(zmq.RCVBUF, 2097152) # 2MB receive buffer

        # Create PUB socket
        self._out_socket = self._zmq_ctx.socket(zmq.PUB)

        # Bind to an address (SUB sockets will connect to this)
        self._out_socket.bind("tcp://*:5555")   # Bind to all interfaces on port 5555

    def start(self):
        """
        :return: None.
        """
        self._init_zmq()

    def run(self):
        """
        :return: None.
        """
        # Connect to the publisher (replace with your publisher's address)
        self._in_socket.connect("tcp://localhost:5556")

        # Subscribe to all messages (empty string) or specific topics
        self._in_socket.setsockopt_string(zmq.SUBSCRIBE, "") # Subscribe to all messages

        gmsk = GMSK(0.5, 4800)

        i_buf = list()
        q_buf = list()
        try:
            while True:
                # Receive data
                raw_data = self._in_socket.recv()

                # Unpack IQ samples
                try:
                    for j in range(0, len(raw_data), 8):
                        i, q = struct.unpack('ff', raw_data[j:j+8])
                        i_buf.append(i)
                        q_buf.append(q)
                except struct.error as e:
                    print(f"Error unpacking data: {e}")

                if len(i_buf) > 225000:
                    # Process IQ samples
                    s_complex = np.array(i_buf) + 1j*np.array(q_buf)
                    i_buf.clear()
                    q_buf.clear()
                    a, b = gmsk.demodulate(225001, s_complex)

        except KeyboardInterrupt:
            print("Subscriber interrupted")
        finally:
            # Clean up
            self._in_socket.close()
            self._out_socket.close()
            self._zmq_ctx.term()
