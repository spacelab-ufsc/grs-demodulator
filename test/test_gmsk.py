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

def add_noise(signal, snr_db):
    """
    Adds AWGN noise to the signal.
    SNR_dB = 10 * log10(Signal_Power / Noise_Power)
    """
    # Calculate signal power
    sig_avg_watts = np.mean(np.abs(signal) ** 2)
    sig_avg_db = 10 * np.log10(sig_avg_watts)
    
    # Calculate noise power
    noise_avg_db = sig_avg_db - snr_db
    noise_avg_watts = 10 ** (noise_avg_db / 10)
    
    # Generate complex noise (for I/Q signal)
    # Divide by sqrt(2) so total power is split between Real and Imag
    noise = np.random.normal(0, np.sqrt(noise_avg_watts/2), len(signal)) + \
            1j * np.random.normal(0, np.sqrt(noise_avg_watts/2), len(signal))
            
    return signal + noise

def bytes_to_bits(data_bytes):
    """
    Helper to convert a list of integers (bytes) to a flat list of bits.
    """
    bits = []
    for b in data_bytes:
        # Convert byte to 8 bits string, then to integers
        bits.extend([int(x) for x in format(b, '08b')])
    return bits

def plot_bit_comparison(tx_bits, rx_bits):
    """
    Plots the original bits (Red) vs Demodulated bits (Blue).
    """
    plt.figure(figsize=(15, 6))
    
    # Limit to first 100 bits
    limit = 100
    t_slice = tx_bits[:limit]
    r_slice = rx_bits[:limit]
    
    # Create x-axis
    x_tx = np.arange(len(t_slice))
    x_rx = np.arange(len(r_slice))

    # Plot Original Bits (Red)
    # Shift y slightly (+0.05) to prevent overlap hiding the lines
    plt.step(x_tx, np.array(t_slice) + 0.05, 'r', where='mid', label='Original Input (Tx)', linewidth=2, alpha=0.8)
    plt.plot(x_tx, np.array(t_slice) + 0.05, 'r.', markersize=8)

    # Plot Demodulated Bits (Blue)
    plt.step(x_rx, np.array(r_slice) - 0.05, 'b', where='mid', label='Demodulated Output (Rx)', linewidth=2, alpha=0.8)
    plt.plot(x_rx, np.array(r_slice) - 0.05, 'b.', markersize=8)

    plt.ylim(-0.5, 1.5)
    plt.yticks([0, 1])
    plt.title("Bit Comparison: Input (Red) vs Output (Blue) - First 100 Bits")
    plt.xlabel("Bit Index")
    plt.ylabel("Logic Level")
    plt.legend(loc='center right')
    plt.grid(True)
    
    plt.savefig("bit_comparison.png")
    plt.close()

def test_modulator_demodulator(verbose = False):
    # Generate data
    data = [random.randint(0, 255) for _ in range(1000)]
    gmsk = GMSK(0.5, 4800)

    # Modulate
    samples, fs, dur = gmsk.modulate(data)

    # Add noise
    # 10dB for moderate noise, 5dB for heavy noise
    samples_noisy = add_noise(samples, snr_db=12) 

    # Demodulate
    demod_bits, signal, _ = gmsk.demodulate(fs, samples_noisy)

    # Re-pack bits into bytes
    data_res = list()
    for i in range(1, len(demod_bits) - 1, 8):
        result = int()
        pos = 8 - 1
        for j in range(8):
            result = result | (demod_bits[i + j] << pos)
            pos -= 1
        data_res.append(result)
        
    if verbose:
        # Convert original bytes to bits for the plot
        tx_bits_flat = bytes_to_bits(data)
        plot_bit_comparison(tx_bits_flat, demod_bits)

    # Assert equality
    assert data == data_res
    
        
if __name__ == "__main__":
    # Set argument to True for plotting the demodulated output bit over the original input bits 
    test_modulator_demodulator(True)