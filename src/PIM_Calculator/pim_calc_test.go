package PIM_Calculator_test

import (
	// "fmt"
    "testing"
    "PIM_Calculator"
)

func TestPIM(t *testing.T) {
    TX := []float32{1980, 1940}
    TX_band := []float32{5, 5}
    im3, im5 := PIM_Calculator.Calculate(TX, TX_band)

    if len(im3.IM) != 4 {
        t.Errorf("IM3 len is: %d, want: %d", len(im3.IM), 4)
    }
    if len(im5.IM) != 6 {
        t.Errorf("IM5 len is: %d, want: %d", len(im5.IM), 6)
    }

    if len(im3.IM) != len(im3.IM_full) {
        t.Errorf("IM3 len is: %d, want: %d", len(im3.IM), len(im3.IM_full))
    }
    if len(im5.IM) != len(im5.IM_full) {
        t.Errorf("IM5 len is: %d, want: %d", len(im5.IM), len(im5.IM_full))
    }

    TX = []float32{1980, 1940, 1950, 1960, 2000}
    TX_band = []float32{5, 5, 5, 5, 5}
    im3, im5 = PIM_Calculator.Calculate(TX, TX_band)

    //fmt.Println("I've got this:\n", im3)
    //fmt.Println("I've got this:\n", im5)
}

func BenchmarkCalculate(b *testing.B) {
    TX := []float32{1980, 1940, 1950, 1960, 2000}
    TX_band := []float32{5, 5, 1.4, 5, 20}
    for i:=0; i<b.N; i++ {
        PIM_Calculator.Calculate(TX, TX_band)
    }
}

func TestCheckRX(t *testing.T) {
    TX := []float32{1980, 1940}
    TX_band := []float32{5, 5}
    im3, im5 := PIM_Calculator.Calculate(TX, TX_band)

    RX := []float32{1900}
    RX_band := []float32{5}
    im_results := PIM_Calculator.CheckRX(RX, RX_band, im3.IM_full)
    if len(im_results) != 1 {
        t.Errorf("IM3 RX hits len is: %d, want: %d", len(im_results), 1)
    }
    im_results = PIM_Calculator.CheckRX(RX, RX_band, im5.IM_full)
    if len(im_results) != 1 {
        t.Errorf("IM5 RX hits len is: %d, want: %d", len(im_results), 1)
    }
}

func BenchmarkCheckRX(b *testing.B) {
    TX := []float32{1980, 1940, 1950, 1960, 2140}
    TX_band := []float32{5, 5, 1.4, 5, 20}
    RX := []float32{1900,1880,1860,1732.5}
    RX_band := []float32{5,5,5,20}

    im3, im5 := PIM_Calculator.Calculate(TX, TX_band)
    for i:=0; i<b.N; i++ {
        PIM_Calculator.CheckRX(RX, RX_band, im3.IM_full)
        PIM_Calculator.CheckRX(RX, RX_band, im5.IM_full)
    }
}
