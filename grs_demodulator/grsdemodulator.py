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

from scipy.signal import lfilter_zi, firwin, lfilter
from grs_demodulator.gmsk import GMSK
from grs_demodulator.timing_sync.mm import MM


class GRSDemodulator:
    """
    Demodulator application.
    """

    DEMOD_DEFAULT_SAMPLE_RATE = int(48e3)
    GMSK_DEFAULT_BAUD_RATE = 4800
    GMSK_DEFAULT_BT = 0.5

    def __init__(self):
        """
        Class constructor.

        :return: None.
        """
        self._baudrate = self.GMSK_DEFAULT_BAUD_RATE
        self._fs = self.DEMOD_DEFAULT_SAMPLE_RATE
        self._bt = self.GMSK_DEFAULT_BT

        self._mod = GMSK(self._bt, self._baudrate)
        self._mm = MM(self._fs, self._baudrate)

        self._build_lpf_taps(self._fs)

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
        self._in_socket.setsockopt_string(
            zmq.SUBSCRIBE, ""
        )  # Subscribe to all messages

        self.samples_buf = bytearray()
        try:
            while True:
                # Receive samples
                raw_data = self._in_socket.recv()

                process_window_in_bytes = (
                    300 * (self._fs / self._bt) * 8 * 8
                )  # 300 bytes in samples

                self.samples_buf.extend(raw_data)

                if len(self.samples_buf) >= process_window_in_bytes:
                    try:
                        bits = self._process_samples(self.samples_buf)

                        # TODO:
                        print(f"demodulated bits: {bits}")
                    except struct.error as e:
                        print(f"Error processing incoming samples: {e}")

                    self.samples_buf.clear()

        except KeyboardInterrupt:
            print("Subscriber interrupted")
        finally:
            # Clean up
            self._in_socket.close()
            self._out_socket.close()
            self._zmq_ctx.term()

    def _init_zmq(self):
        """
        :return: None.
        """
        # Prepare ZMQ context and socket
        self._zmq_ctx = zmq.Context()

        # Create SUB socket
        self._in_socket = self._zmq_ctx.socket(zmq.SUB)

        # Optimizations
        self._in_socket.setsockopt(zmq.RCVHWM, 1000000)  # High water mark
        self._in_socket.setsockopt(zmq.RCVBUF, 2097152)  # 2MB receive buffer

        # Create PUB socket
        self._out_socket = self._zmq_ctx.socket(zmq.PUB)

        # Bind to an address (SUB sockets will connect to this)
        self._out_socket.bind("tcp://*:5555")  # Bind to all interfaces on port 5555

    def _process_samples(self, buf: bytearray):
        """
        Process incoming samples.
        :param buf:
        :type: buffer with interleaved float32 IQ samples

        :return: demodulated bits
        :rtype:
        """
        samples = np.frombuffer(buf, dtype=np.complex64)

        filtered_samples, self._zi = lfilter(self._taps, [1.0], samples, zi=self._zi)

        soft_symbols, _ = self._mod.demodulate(self._fs, filtered_samples)

        bits = self._mm.decode_stream(soft_symbols)

        return list(map(int, bits))

    def _build_lpf_taps(self, fs, window="hamming", beta=6.76):
        """
        Calculte low pass FIR filter taps and initial state for continuous processing.
        """
        cutoff = 1.2 * self._baudrate
        transition = 2.5 * cutoff

        num_taps = int(np.ceil(4 * fs / transition))
        if num_taps % 2 == 0:
            num_taps += 1  # Make odd

        self._taps = firwin(
            num_taps,
            cutoff,
            window=(window, beta) if window == "kaiser" else window,
            fs=fs,
            pass_zero="lowpass",
        )

        self._zi = lfilter_zi(self._taps, [1.0]) * 0.0
