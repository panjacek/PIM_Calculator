"""Pure-Mojo PIM calculator library.

Native port of python/PIM_Calculator/pim_calc.py producing the shared JSON
contract byte-compatibly (identical row ordering via full-record sorting).
"""

from std.utils import StaticTuple


comptime DEFAULT_BANDWIDTH = 5.0


@fieldwise_init
struct IM3Record(Comparable, Copyable, Equatable, Movable):
    """One IM3 product row. Field order mirrors the python structured dtype
    (IM, IM_COMP, IM_FULL) so lexicographic record comparison reproduces
    np.unique(axis=0) semantics exactly."""

    var im: Float64
    var src: StaticTuple[Float64, 3]
    var band_min: Float64
    var band_max: Float64

    def __eq__(self, other: Self) -> Bool:
        if self.im != other.im:
            return False
        for i in range(3):
            if self.src[i] != other.src[i]:
                return False
        return (
            self.band_min == other.band_min and self.band_max == other.band_max
        )

    def __lt__(self, other: Self) -> Bool:
        if self.im != other.im:
            return self.im < other.im
        for i in range(3):
            if self.src[i] != other.src[i]:
                return self.src[i] < other.src[i]
        if self.band_min != other.band_min:
            return self.band_min < other.band_min
        return self.band_max < other.band_max


@fieldwise_init
struct IM5Record(Comparable, Copyable, Equatable, Movable):
    """One IM5 product row; same layout as IM3Record with 5 sources."""

    var im: Float64
    var src: StaticTuple[Float64, 5]
    var band_min: Float64
    var band_max: Float64

    def __eq__(self, other: Self) -> Bool:
        if self.im != other.im:
            return False
        for i in range(5):
            if self.src[i] != other.src[i]:
                return False
        return (
            self.band_min == other.band_min and self.band_max == other.band_max
        )

    def __lt__(self, other: Self) -> Bool:
        if self.im != other.im:
            return self.im < other.im
        for i in range(5):
            if self.src[i] != other.src[i]:
                return self.src[i] < other.src[i]
        if self.band_min != other.band_min:
            return self.band_min < other.band_min
        return self.band_max < other.band_max


@fieldwise_init
struct RxHit(Copyable, Movable):
    """One RX-band/PIM overlap finding."""

    var rx_min: Float64
    var rx_max: Float64
    var pim_min: Float64
    var pim_max: Float64
    var src_desc: String

    def describe(self) -> String:
        return (
            String(self.rx_min)
            + "-"
            + String(self.rx_max)
            + " is inside: "
            + String(self.pim_min)
            + "-"
            + String(self.pim_max)
            + ", TX src: "
            + self.src_desc
        )


def default_bands(count: Int) -> List[Float64]:
    """Bandwidth list of `count` 5 MHz entries (LTE5 default)."""
    var bands = List[Float64]()
    for _ in range(count):
        bands.append(DEFAULT_BANDWIDTH)
    return bands^


def _normalize_bands(
    carriers: List[Float64], bandwidths: List[Float64]
) raises -> List[Float64]:
    """Match python semantics: mismatched length reuses the first value."""
    if len(bandwidths) == 0:
        raise Error("empty bandwidth list")
    var bands = List[Float64]()
    if len(bandwidths) == len(carriers):
        for value in bandwidths:
            bands.append(value)
    else:
        var first = bandwidths[0]
        for _ in range(len(carriers)):
            bands.append(first)
    return bands^


def _distinct_count(values: List[Float64]) -> Int:
    var count = 0
    for i in range(len(values)):
        var duplicate = False
        for j in range(i):
            if values[j] == values[i]:
                duplicate = True
        if not duplicate:
            count += 1
    return count


def _as_list(t: StaticTuple[Float64, 3]) -> List[Float64]:
    var out = List[Float64]()
    for i in range(3):
        out.append(t[i])
    return out^


def _as_list5(t: StaticTuple[Float64, 5]) -> List[Float64]:
    var out = List[Float64]()
    for i in range(5):
        out.append(t[i])
    return out^


def _sorted_unique[
    T: Comparable & Copyable & Deinitable
](raw: List[T],) -> List[T]:
    """In-place sort of a span view over `raw`, then adjacent dedupe.

    Full-record ordering equals np.unique(axis=0) because __lt__/__eq__
    cover every field in python dtype order.
    """
    var data = raw.copy()
    var view = Span(data)
    sort(view)
    var out = List[T]()
    if len(view) == 0:
        return out^
    out.append(view[0].copy())
    for idx in range(1, len(view)):
        if view[idx] != out[len(out) - 1]:
            out.append(view[idx].copy())
    return out^


def _clean_im3(raw: List[IM3Record]) -> List[IM3Record]:
    """np.unique(axis=0) then drop products with <2 distinct TX sources
    (= python _clean_array rule)."""
    var unique = _sorted_unique(raw)
    var out = List[IM3Record]()
    for record in unique:
        if _distinct_count(_as_list(record.src)) >= 2:
            out.append(record.copy())
    return out^


def _clean_im5(raw: List[IM5Record]) -> List[IM5Record]:
    var unique = _sorted_unique(raw)
    var out = List[IM5Record]()
    for record in unique:
        if _distinct_count(_as_list5(record.src)) >= 2:
            out.append(record.copy())
    return out^


def calculate(
    tx_list: List[Float64],
    tx_bandwidths: List[Float64],
    max_order: Int = 5,
) raises -> Tuple[List[IM3Record], List[IM5Record]]:
    """Port of PIMCalc.calculate(). Loop structure copied verbatim:
    IM3 i<=j, k free; IM5 i<=j, k free, l>=j, m>=k with value order
    [i, j, l, k, m]."""
    if len(tx_list) < 1:
        raise Error("tx_list must contain at least one carrier")
    var bands = _normalize_bands(tx_list, tx_bandwidths)
    var n = len(tx_list)

    var im3_raw = List[IM3Record]()
    var im5_raw = List[IM5Record]()

    for i in range(n):
        for j in range(i, n):
            for k in range(n):
                var centre3 = tx_list[i] + tx_list[j] - tx_list[k]
                var band3 = bands[i] + bands[j] + bands[k]
                im3_raw.append(
                    IM3Record(
                        centre3,
                        StaticTuple[Float64, 3](
                            tx_list[i], tx_list[j], tx_list[k]
                        ),
                        centre3 - band3 / 2.0,
                        centre3 + band3 / 2.0,
                    )
                )
                if max_order <= 3:
                    continue
                for l in range(j, n):
                    for m in range(k, n):
                        var centre5 = (
                            tx_list[i]
                            + tx_list[j]
                            + tx_list[l]
                            - tx_list[k]
                            - tx_list[m]
                        )
                        var band5 = (
                            bands[i] + bands[j] + bands[l] + bands[k] + bands[m]
                        )
                        im5_raw.append(
                            IM5Record(
                                centre5,
                                StaticTuple[Float64, 5](
                                    tx_list[i],
                                    tx_list[j],
                                    tx_list[l],
                                    tx_list[k],
                                    tx_list[m],
                                ),
                                centre5 - band5 / 2.0,
                                centre5 + band5 / 2.0,
                            )
                        )

    return (_clean_im3(im3_raw), _clean_im5(im5_raw))


def check_rx(
    rx_list: List[Float64],
    rx_bandwidths: List[Float64],
    pim_records: List[IM3Record],
) raises -> List[RxHit]:
    """RX affected by PIM if either PIM edge lies inside the RX band or the
    PIM fully covers the RX band (verbatim port of PIMCalc.check_rx)."""
    var bands = _normalize_bands(rx_list, rx_bandwidths)
    var hits = List[RxHit]()
    for x in range(len(rx_list)):
        var rx_min = rx_list[x] - bands[x] / 2.0
        var rx_max = rx_list[x] + bands[x] / 2.0
        for e in range(len(pim_records)):
            var hit_count = 0
            if (
                rx_min <= pim_records[e].band_min
                and pim_records[e].band_min <= rx_max
            ):
                hit_count += 1
            if (
                rx_min <= pim_records[e].band_max
                and pim_records[e].band_max <= rx_max
            ):
                hit_count += 1
            if (
                pim_records[e].band_min <= rx_min
                and rx_max <= pim_records[e].band_max
            ):
                hit_count += 1
            if hit_count > 0:
                hits.append(
                    RxHit(
                        rx_min,
                        rx_max,
                        pim_records[e].band_min,
                        pim_records[e].band_max,
                        _format_src(pim_records[e].src),
                    )
                )
    return hits^


def check_rx_im5(
    rx_list: List[Float64],
    rx_bandwidths: List[Float64],
    pim_records: List[IM5Record],
) raises -> List[RxHit]:
    var bands = _normalize_bands(rx_list, rx_bandwidths)
    var hits = List[RxHit]()
    for x in range(len(rx_list)):
        var rx_min = rx_list[x] - bands[x] / 2.0
        var rx_max = rx_list[x] + bands[x] / 2.0
        for e in range(len(pim_records)):
            var hit_count = 0
            if (
                rx_min <= pim_records[e].band_min
                and pim_records[e].band_min <= rx_max
            ):
                hit_count += 1
            if (
                rx_min <= pim_records[e].band_max
                and pim_records[e].band_max <= rx_max
            ):
                hit_count += 1
            if (
                pim_records[e].band_min <= rx_min
                and rx_max <= pim_records[e].band_max
            ):
                hit_count += 1
            if hit_count > 0:
                hits.append(
                    RxHit(
                        rx_min,
                        rx_max,
                        pim_records[e].band_min,
                        pim_records[e].band_max,
                        _format_src5(pim_records[e].src),
                    )
                )
    return hits^


def _format_src(t: StaticTuple[Float64, 3]) -> String:
    var out = String("")
    for i in range(3):
        if i > 0:
            out += " "
        out += String(t[i])
    return out


def _format_src5(t: StaticTuple[Float64, 5]) -> String:
    var out = String("")
    for i in range(5):
        if i > 0:
            out += " "
        out += String(t[i])
    return out


def _floats_json(values: List[Float64]) -> String:
    var out = String("[")
    for i in range(len(values)):
        if i > 0:
            out += ", "
        out += String(values[i])
    out += "]"
    return out


def _rows_json(
    im_values: List[Float64],
    mins: List[Float64],
    maxs: List[Float64],
) -> String:
    var out = String("[")
    for i in range(len(im_values)):
        if i > 0:
            out += ", "
        out += '{"cf": ' + String(im_values[i])
        out += ', "min": ' + String(mins[i])
        out += ', "max": ' + String(maxs[i]) + "}"
    out += "]"
    return out


def results_to_json(
    im3: List[IM3Record],
    im5: List[IM5Record],
    tx_list: List[Float64],
    rx_list: List[Float64],
) -> String:
    """Shared JSON contract across flavours:

        {"tx_list": [...], "rx_list": [...],
         "IM3": [{"cf": .., "min": .., "max": ..}, ...], "IM5": [...]}

    Row order matches the python flavour exactly.
    """
    var im3_cf = List[Float64]()
    var im3_min = List[Float64]()
    var im3_max = List[Float64]()
    for record in im3:
        im3_cf.append(record.im)
        im3_min.append(record.band_min)
        im3_max.append(record.band_max)

    var im5_cf = List[Float64]()
    var im5_min = List[Float64]()
    var im5_max = List[Float64]()
    for record in im5:
        im5_cf.append(record.im)
        im5_min.append(record.band_min)
        im5_max.append(record.band_max)

    var out = String("{\n")
    out += '  "tx_list": ' + _floats_json(tx_list) + ",\n"
    out += '  "rx_list": ' + _floats_json(rx_list) + ",\n"
    out += '  "IM3": ' + _rows_json(im3_cf, im3_min, im3_max) + ",\n"
    out += '  "IM5": ' + _rows_json(im5_cf, im5_min, im5_max) + "\n"
    out += "}"
    return out


def _append_table(
    mut lines: List[String],
    name: String,
    cf: List[Float64],
    mins: List[Float64],
    maxs: List[Float64],
    srcs: List[String],
):
    var bar = ""
    for _ in range(48):
        bar += "="
    lines.append(bar)
    lines.append(name + ": PIM Cf | f min  | f max  | TX source")
    for i in range(len(cf)):
        lines.append(
            String(cf[i])
            + " | "
            + String(mins[i])
            + " | "
            + String(maxs[i])
            + " | "
            + srcs[i]
        )
    lines.append(bar)


def get_results(
    tx_list: List[Float64],
    tx_bandwidths: List[Float64],
    rx_list: List[Float64],
    rx_bandwidths: List[Float64],
    max_order: Int = 5,
) raises -> List[String]:
    """Calculate + human-readable text table (+ RX check when rx_list is
    non-empty). Cosmetic drift vs the python text output is accepted."""
    var result = calculate(tx_list, tx_bandwidths, max_order)
    var lines = List[String]()

    var im3_cf = List[Float64]()
    var im3_min = List[Float64]()
    var im3_max = List[Float64]()
    var im3_src = List[String]()
    for record in result[0]:
        im3_cf.append(record.im)
        im3_min.append(record.band_min)
        im3_max.append(record.band_max)
        im3_src.append(_format_src(record.src))
    _append_table(lines, "IM3", im3_cf, im3_min, im3_max, im3_src)

    var im5_cf = List[Float64]()
    var im5_min = List[Float64]()
    var im5_max = List[Float64]()
    var im5_src = List[String]()
    for record in result[1]:
        im5_cf.append(record.im)
        im5_min.append(record.band_min)
        im5_max.append(record.band_max)
        im5_src.append(_format_src5(record.src))
    _append_table(lines, "IM5", im5_cf, im5_min, im5_max, im5_src)

    if len(rx_list) > 0:
        var im3_hits = check_rx(rx_list, rx_bandwidths, result[0])
        var im5_hits = check_rx_im5(rx_list, rx_bandwidths, result[1])
        lines.append("==== RX check ===")
        for hit in im3_hits:
            lines.append("IM3: " + hit.describe())
        for hit in im5_hits:
            lines.append("IM5: " + hit.describe())

    return lines^
