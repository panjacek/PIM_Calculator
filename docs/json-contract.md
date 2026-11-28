# JSON output contract

Single source of truth for the `--output_file` schema shared by all four
flavours. Producers emit this shape; consumers may rely on it.

## Schema

```json
{
  "tx_list": [2152.0, 1932.0],
  "rx_list": [1752.0, 1900.0],
  "IM3": [{"cf": 1712.0, "min": 1704.5, "max": 1719.5}],
  "IM5": [{"cf": 1492.0, "min": 1479.5, "max": 1504.5}]
}
```

| key | type | meaning |
| --- | --- | --- |
| `tx_list` | list of float | TX carriers, echoed as given (MHz) |
| `rx_list` | list of float | RX carriers, echoed as given (MHz) |
| `IM3` / `IM5` | list of row | one row per intermodulation product |

Row fields: `cf` = IM centre frequency, `min`/`max` = `cf ± band/2` (MHz).

## Producers and consumers

| role | code |
| --- | --- |
| producer (python) | `python/PIM_Calculator/pim_calc.py::results_to_json` |
| producer (go) | `go/PIM_Calculator/pim_calc.go::write_results` |
| producer (mojo) | `mojo/pim_calc.mojo::results_to_json` (interop wrapper `pim_calc_py.mojo` writes through the python one) |
| consumers | `web/pim_web.py`, `tests/test_integration.py` |

## Known flavour divergences

Documented, intentional-until-decided differences. Tests assert them
explicitly (`tests/test_integration.py`).

| topic | python / mojo | go |
| --- | --- | --- |
| float width | float64 | float32 (display rounding) |
| duplicate rows | kept per distinct TX source (e.g. 10 IM5 rows) | deduped by `cf` only (e.g. 6 IM5 rows) |
| `rx_list` omitted | echoed as `[]` | injected default `[1900]` |
| single TX carrier | no rows (no products) | one self-product row |
| non-numeric `tx_list` | error message, exit 1 | panic, exit 2 |
| unparsable value inside RX list | error message, exit 1 | value dropped; panics (exit 2) if surviving RX count exceeds `-rx_band` length (default `-rx_band 5` is single) |
| unwritable `--output_file` | error message, exit 1 | error logged, exit 0 |

Centre frequencies and `(cf, min, max)` row *sets* agree across all
flavours for every case except the single-TX one above.

## Flag syntax notes

- python accepts `--flag value` and `--flag=value`; the mojo CLIs only
  support the space form (`--output_file PATH`).
- go's `flag` package stops at the first non-flag argument: flags must
  precede the positional TX list (`-rx_list ... 2152,1932`).

## References

- README: "CLI usage" (argument table, example payload, bad-input table)
- `python/PIM_Calculator/pim_calc.py::results_to_json` docstring
- `mojo/pim_calc.mojo::results_to_json` docstring
