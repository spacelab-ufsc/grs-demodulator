#
#  test_gmsk.py
#  
#  Copyright The GRS Demodulator Contributors.
#  
#  This file is part of SpaceLab-Transmitter.
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
#  License along with GRS Dedmodulator; if not, see <http://www.gnu.org/licenses/>.
#  
#

import random
import matplotlib.pyplot as plt
import numpy as np

from grs_demodulator.gmsk import GMSK

def plot_timesync_output(trace, soft_symbols, sps):
    
    plt.figure(figsize=(12, 6))
    
    # Plot the continuous signal
    plt.plot(trace, label='Discriminator Output', color='lightgray', linewidth=1)
    
    # Plot the samples taken
    x_indices = np.arange(0, len(soft_symbols)) * sps + (sps/2) 
    
    # Limit to first 50 bits
    limit = 50
    plt.scatter(x_indices[:limit], soft_symbols[:limit], color='red', zorder=5, label='TimeSync Samples')
    plt.plot(trace[:int(limit*sps)], color='blue', alpha=0.5)
    plt.xlim(0, limit*sps)
    
    # 3. Draw the Decision Line
    plt.axhline(0, color='black', linestyle='--')
    
    plt.title("Trace vs Sampling Points")
    plt.legend()
    plt.grid(True)
    plt.savefig("timesync_decision.png")
    plt.close()

def test_modulator_demodulator(verbose = False):
    data = [random.randint(0, 255) for _ in range(1000)]
    
    gmsk = GMSK(0.5, 4800)

    samples, fs, dur = gmsk.modulate(data)

    demod_bits, signal, freq_dev = gmsk.demodulate(fs, samples)

    data_res = list()

    for i in range(1, len(demod_bits) - 1, 8):
        result = int()
        pos = 8 - 1
        for j in range(8):
            result = result | (demod_bits[i + j] << pos)
            pos -= 1
        data_res.append(result)
        
    if verbose:
        plot_timesync_output(freq_dev, signal, int(fs/4800))
    
        
if __name__ == "__main__":
    # Set argument to True for plotting timesync decisions over the trace
    test_modulator_demodulator(True)
