package main

import (
    "os"
    "fmt"
    "log"
    "strconv"
    "strings"
)

// configuration for main calculate
type config struct {
    freq []float32
    band []float32
}

// results struct
type im_results struct {
    IM []float32
    IM_full [][]float32
}

// divider print
func print_div(character string, num int) {
    for e:=0; e < num; e++ {
        fmt.Print(character)
    }
    fmt.Print("\n")
}

// converts string into list of floats
func convert_arg(item string) ([]float32) {
    items := strings.Split(item, ",")

    result := make([]float32, 0)
    for i:=0; i < len(items); i++ {
        res, err := strconv.ParseFloat(items[i], 32)
        if err != nil {
            // do something sensible
        } else {
            result = append(result, float32(res))
        }
    }
    return result
}

// Read cmd line args
func read_args() (config, config) {
    args_len := len(os.Args)
    TX := convert_arg(os.Args[1])
    var TX_band []float32
    if args_len >= 3 {
        TX_band = convert_arg(os.Args[2])
    } else {
        TX_band = make([]float32, len(TX))
        for i := range(TX) {
            TX_band[i] = 5.0
        }
    }

    if args_len < 4 {
        return config{TX, TX_band}, config{TX, TX_band}
    }

    RX := convert_arg(os.Args[3])
    var RX_band []float32
    if args_len >= 5 {
        RX_band = convert_arg(os.Args[4])
    } else {
        RX_band = make([]float32, len(RX))
        for i := range(RX) {
            RX_band[i] = 5.0
        }
    }

    return config{TX, TX_band}, config{RX, RX_band}
}


func get_im3(tx1 float32, tx2 float32, tx3 float32) (float32) {
    return tx1 + tx2 - tx3
}

func get_im5(tx1 float32, tx2 float32, tx3 float32, tx4 float32, tx5 float32) (float32) {
    return tx1 + tx2 + tx3 - tx4 - tx5
}

func remove_duplicates(elements []float32) ([]float32){
    // Use map to record duplicates as we find them.
    encountered := map[float32]bool{}
    result := []float32{}

    for v := range elements {
        if encountered[elements[v]] == true {
            // Do not add duplicate.
        } else {
            // Record this element as an encountered element.
            encountered[elements[v]] = true
            // Append to result slice.
            result = append(result, elements[v])
        }
    }
    // Return the new slice.
    return result
}

func calculate(TX []float32, TX_band []float32) (im_results, im_results) {
    fmt.Println("TX:", TX)
    fmt.Println("TX_bands:", TX_band)
    print_div("-", 80)

    if len(TX_band) != len(TX) {
        log.Printf("%v", fmt.Errorf("SHIT HAPPENED"))
        panic("")
    }

    tx_len := len(TX)
    max_order := 5

    // init 'arrays'
    IM3 := make([]float32, 0)
    IM3_band := make([]float32, 0)

    IM5 := make([]float32, 0)
    IM5_band := make([]float32, 0)

    // iterate over
    for i := 0; i < tx_len; i++ {
        im_order_cnt := 0
        for j := 0; j < tx_len; j++ {
            for k := 0; k < tx_len; k++ {
                im_order_cnt = 3
                IM3 = append(IM3, get_im3(TX[i], TX[j], TX[k]))
                IM3_band = append(IM3_band, TX_band[i] + TX_band[j] + TX_band[k])

                if max_order == im_order_cnt {
                    continue
                }
                for l := 0; l < tx_len; l++ {
                    for m := 0; m < tx_len; m++ {
                        im_order_cnt = 5
                        IM5 = append(IM5, get_im5(TX[i], TX[j], TX[k], TX[l], TX[m]))
                        IM5_band = append(IM5_band, TX_band[i] + TX_band[j] + TX_band[k] + TX_band[l] + TX_band[m])
                    }
                }
            }
        }
    }
    // fmt.Println(IM3)
    // fmt.Println(IM3_band)
    // fmt.Println(IM5)
    // fmt.Println(IM5_band)

    // clean the duplicates
    IM3 = remove_duplicates(IM3)
    IM5 = remove_duplicates(IM5)

    im3_len := len(IM3)
    IM3_full := make([][]float32, 0)
    im5_len := len(IM5)
    IM5_full := make([][]float32, 0)

    // IM f0 - band, f0 + band
    for i := 0; i < im5_len; i++ {
        if i < im3_len {
            im_tmp := [][]float32{{IM3[i] - IM3_band[i]/2.0, IM3[i] + IM3_band[i]/2.0}}
            IM3_full = append(IM3_full, im_tmp...)
        }
        if max_order == 5 {
            im_tmp := [][]float32{{IM5[i] - IM5_band[i]/2.0, IM5[i] + IM5_band[i]/2.0}}
            IM5_full = append(IM5_full, im_tmp...)
        }
    }
    print_div("-", 80)
    // fmt.Println(IM3_full)
    // fmt.Println(IM5_full)

    return im_results{IM3, IM3_full}, im_results{IM5, IM5_full}
}

func check_rx(rx []float32, rx_band []float32, im_full [][]float32) [][]float32 {
    im_hits := make([][]float32, 0)
    for i := range(rx) {
        rx_min := rx[i] - rx_band[i]/2
        rx_max := rx[i] + rx_band[i]/2
        for im := range(im_full) {
            hits := 0
            pim := []float32{im_full[im][0], im_full[im][1]}
            if im_full[im][0] <= rx_min && rx_min <= im_full[im][1] {
                hits++
            }
            if im_full[im][0] <= rx_max && rx_max <= im_full[im][1] {
                hits++
            }
            if hits > 0 {
                im_hits = append(im_hits, []float32{rx[i], pim[0], pim[1]})
            }
        }
    }
    return im_hits
}


// TODO: write some decent tests later...
func testme() {
    TX := []float32{1980, 1940}
    TX_band := []float32{5, 5}
    im3, im5 := calculate(TX, TX_band)

    fmt.Println("I've got this:\n", im3)
    fmt.Println("I've got this:\n", im5)


    TX = []float32{1980, 1940, 1950, 1960, 2000}
    TX_band = []float32{5, 5, 5, 5, 5}
    im3, im5 = calculate(TX, TX_band)

    fmt.Println("I've got this:\n", im3)
    fmt.Println("I've got this:\n", im5)
}

func main() {
    print_div("-", 80)
    fmt.Println("|\tThis is PIMC calc")
    print_div("-", 80)
    args := os.Args[1:]

    if len(args) < 1 {
        log.Printf("%v", fmt.Errorf("I need at least TX list"))
        fmt.Println("Unit Tests")
        testme()
    } else {
        args_TX, args_RX := read_args()
        im3, im5 := calculate(args_TX.freq, args_TX.band)

        fmt.Println("I've got this IM3:\n", im3)
        print_div("-", 80)
        fmt.Println("I've got this IM5:\n", im5)
        print_div("-", 80)

        if len(args) > 3 {
            im_results := check_rx(args_RX.freq, args_RX.band, im3.IM_full)
            for i:= range(im_results) {
                fmt.Printf("%f is affected by %f\n", im_results[i][0], im_results[i][1:])
            }
            print_div("-", 80)
            im_results = check_rx(args_RX.freq, args_RX.band, im5.IM_full)
            for i:= range(im_results) {
                fmt.Printf("%f is affected by %f\n", im_results[i][0], im_results[i][1:])
            }
        }

    }
}
