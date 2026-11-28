package PIM_Calculator

import (
	"encoding/json"
	"flag"
	"os"
	"path/filepath"
	"testing"
)

// withArgs points the default flag set at args for one test.
func withArgs(t *testing.T, args ...string) {
	t.Helper()
	oldArgs := os.Args
	oldCommandLine := flag.CommandLine
	os.Args = append([]string{"pim_calc"}, args...)
	flag.CommandLine = flag.NewFlagSet(os.Args[0], flag.ContinueOnError)
	t.Cleanup(func() {
		os.Args = oldArgs
		flag.CommandLine = oldCommandLine
	})
}

func TestReadArgs(t *testing.T) {
	withArgs(t,
		"-tx_band", "5,10",
		"-rx_list", "1752,1900",
		"-rx_band", "5,5",
		"-output_file", "out.json",
		"2152,1932",
	)
	tx, rx, out := read_args()

	if len(tx.freq) != 2 || tx.freq[0] != 2152 || tx.freq[1] != 1932 {
		t.Errorf("tx freq = %v, want [2152 1932]", tx.freq)
	}
	if len(tx.band) != 2 || tx.band[0] != 5 || tx.band[1] != 10 {
		t.Errorf("tx band = %v, want [5 10]", tx.band)
	}
	if len(rx.freq) != 2 || rx.freq[0] != 1752 || rx.freq[1] != 1900 {
		t.Errorf("rx freq = %v, want [1752 1900]", rx.freq)
	}
	if *out != "out.json" {
		t.Errorf("output_file = %q, want out.json", *out)
	}
}

func TestReadArgsDefaults(t *testing.T) {
	withArgs(t, "1980,1940")
	tx, rx, out := read_args()

	// Known divergence: go injects rx_list=1900 when the flag is omitted,
	// python/mojo echo [] (see docs/json-contract.md).
	if len(rx.freq) != 1 || rx.freq[0] != 1900 {
		t.Errorf("default rx = %v, want [1900]", rx.freq)
	}
	if len(tx.band) != 2 || tx.band[0] != 5 || tx.band[1] != 5 {
		t.Errorf("default tx band = %v, want [5 5]", tx.band)
	}
	if *out != "" {
		t.Errorf("output_file = %q, want empty", *out)
	}
}

func TestWriteResults(t *testing.T) {
	path := filepath.Join(t.TempDir(), "out.json")
	im3, im5 := Calculate([]float32{1980, 1940}, []float32{5, 5})
	write_results(path,
		config{freq: []float32{1980, 1940}, band: []float32{5, 5}},
		config{freq: []float32{1900}, band: []float32{5}},
		im3, im5,
	)

	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read output: %v", err)
	}
	var payload pim_output
	if err := json.Unmarshal(data, &payload); err != nil {
		t.Fatalf("parse output: %v", err)
	}

	if len(payload.Tx_list) != 2 || payload.Tx_list[0] != 1980 {
		t.Errorf("tx_list = %v, want [1980 1940]", payload.Tx_list)
	}
	if len(payload.Rx_list) != 1 || payload.Rx_list[0] != 1900 {
		t.Errorf("rx_list = %v, want [1900]", payload.Rx_list)
	}
	if len(payload.IM3) != 4 || len(payload.IM5) != 6 {
		t.Errorf("rows IM3=%d IM5=%d, want 4/6", len(payload.IM3), len(payload.IM5))
	}
	for _, row := range payload.IM3 {
		if row.Min >= row.Max {
			t.Errorf("bad IM3 row %+v: min >= max", row)
		}
	}
}
