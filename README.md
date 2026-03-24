<h1 align="center">
    GRS Demodulator
    <br>
</h1>

<h4 align="center">GMSK Demodulator of the SpaceLab's Ground Station.</h4>

<p align="center">
    <a href="https://github.com/spacelab-ufsc/grs-demodulator">
        <img src="https://img.shields.io/badge/status-development-green?style=for-the-badge">
    </a>
    <a href="https://github.com/spacelab-ufsc/grs-demodulator/releases">
        <img alt="GitHub commits since latest release (by date)" src="https://img.shields.io/github/commits-since/spacelab-ufsc/grs-demodulator/latest?style=for-the-badge">
    </a>
    <a href="https://github.com/spacelab-ufsc/grs-demodulator/blob/main/LICENSE">
        <img src="https://img.shields.io/badge/license-GPL3-yellow?style=for-the-badge">
    </a>
</p>

<p align="center">
    <a href="#overview">Overview</a> •
    <a href="#dependencies">Dependencies</a> •
    <a href="#installing">Installing</a> •
    <a href="#documentation">Documentation</a> •
    <a href="#license">License</a>
</p>

## Overview

The GRS Demodulator is a GMSK (Gaussian Minimum Shift Keying) demodulator for SpaceLab's Ground Station signal processing pipeline. It sits between the IQ Receiver and the downstream syncword detector and decoder, receiving a continuous stream of complex IQ samples and outputting a recovered bitstream.

The demodulation pipeline consists of a frequency discriminator, a Gaussian matched filter, symbol timing recovery, and hard-decision thresholding. Both modulation and demodulation are implemented, allowing the GMSK module to be used standalone for testing and simulation.

### Demodulation Pipeline

1. **Frequency Discriminator**: Extracts instantaneous frequency deviations from the phase derivative of the complex IQ samples.
2. **Gaussian Matched Filter**: Applies a Gaussian filter matched to the BT product to reduce inter-symbol interference.
3. **Normalization**: Centers and scales the filtered signal for reliable symbol decisions.
4. **Timing Recovery**: Synchronizes the sampling instants to the symbol boundaries.
5. **Hard Decision**: Thresholds the recovered soft symbols into a binary bitstream.

## Dependencies

* [numpy](https://pypi.org/project/numpy/) (>= 2.3.5)
* [scipy](https://pypi.org/project/scipy/) (>= 1.15.2)
* [pyzmq](https://pypi.org/project/pyzmq/) (>= 25.1.1)

### Installation on Ubuntu

```
sudo apt install python3 python3-numpy python3-scipy python3-zmq
```

### Installation on Fedora

```
sudo dnf install python3 python3-numpy python3-scipy python3-zmq
```

### Installation via pip

```
pip install -r requirements.txt
```

> **Note:** `matplotlib` is required only for running the GMSK test script (`test_gmsk.py`), which plots a visual comparison of transmitted and demodulated bits. It is not needed for normal operation.

## Installing

```
python setup.py install
```

## Documentation

The documentation of this project is generated using the Sphinx tool, and it is available [here](https://spacelab-ufsc.github.io/grs-demodulator/).

### Dependencies

* Sphinx
* sphinx-rtd-theme

### Building the Documentation

```
make html
```

## License

This project is licensed under GPLv3 license.
