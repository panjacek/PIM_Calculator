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

Reference implementation: `python/PIM_Calculator/pim_calc.py`.
