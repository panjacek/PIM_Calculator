# What is PIM?

PIM (Passive Intermodulation) is unwanted interference generated when two or
more strong TX signals pass through a non-linear passive component
(connector, cable, antenna). The mixing products land at frequencies given by
combinations of the carrier frequencies and can fall inside a receive band,
desensitising the uplink.

- Definition and background: [Wikipedia: Intermodulation](https://en.wikipedia.org/wiki/Intermodulation)
  (PIM is intermodulation from *passive* devices)
- Field measurement practice: [Wikipedia: Passive Intermodulation](https://en.wikipedia.org/wiki/Passive_intermodulation)

## Products calculated here

Given TX carriers `f1..fn`, this tool computes:

| product | center frequency | notes |
| ------- | ---------------- | ----- |
| IM3     | `f_i + f_j - f_k` over TX carrier index combinations | closest-in, usually dominant |
| IM5     | `f_i + f_j + f_l - f_k - f_m` over index combinations | lower level, still checked |

Each product gets a frequency span: the sum of participating carrier
bandwidths, centred on the computed frequency. A product "hits" when its span
overlaps an RX band.

### Worked example

For two 5 MHz TX carriers at `2152` MHz and `1932` MHz:

- One IM3 product is `2152 + 1932 - 2152 = 1932` MHz (with span `5 + 5 + 5 = 15` MHz, i.e. `1924.5–1939.5` MHz).
- Another IM3 product is `2 * 1932 - 2152 = 1712` MHz (span `1704.5–1719.5` MHz).
- If an RX band is `1752` MHz (5 MHz wide, `1749.5–1754.5` MHz), neither overlaps; if an RX band is `1930` MHz, `1932` MHz hits.

Reference implementation: `python/PIM_Calculator/pim_calc.py`.
