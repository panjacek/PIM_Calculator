PIM Calculator
=============

Calculate PIM for RF antennas

[![Build Status](https://travis-ci.com/panjacek/PIM_Calculator.svg?branch=master)](https://travis-ci.com/panjacek/PIM_Calculator)

Usage Examples:
=============

**pim_calc.py**    [-h] [--tx_size TX_SIZE] [-r RX_LIST] [--rx_size RX_SIZE]
                   [--log_lvl LOG_LVL]
                   tx_list

Calculates PIM for RF antennas with FDD

| positional | description |
| ---------- | ----------- |
| tx_list    | List of TX Carriers |


| optional argument | description |
| ----------------- | ----------- |
| -h, --help        | show this help message and exit |
| --tx_size TX_SIZE | List of TX Carriers bands [5MHz] |
| -r RX_LIST, --rx_list RX_LIST | List of RX Carriers |
| --rx_size RX_SIZE | List of RX Carriers bands [5MHz] |
| --log_lvl LOG_LVL | logger level to display [INFO] |

