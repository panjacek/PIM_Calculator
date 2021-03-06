package PIM_Calculator

import (
    //"os"
    "fmt"
    "log"
    "strconv"
    "strings"
    "flag"
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
    TX_band := flag.String("tx_band", "5,5", "List of TX bands")
    RX := flag.String("rx_list", "1900", "List of RXs")
    RX_band := flag.String("rx_band", "5", "List of RX bands")

    // Parse arguments
    flag.Parse()
    //tx_list := convert_arg(*TX)
    tx_list := convert_arg(flag.Args()[0])
    tx_band := convert_arg(*TX_band)
    rx_list := convert_arg(*RX)
    rx_band := convert_arg(*RX_band)

    fmt.Println("TX_list = ", tx_list)
    fmt.Println("TX_band = ", tx_band)
    fmt.Println("RX_list = ", rx_list)
    fmt.Println("RX_band = ", rx_band)
    return config{tx_list, tx_band}, config{rx_list, rx_band}
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

func Calculate(TX []float32, TX_band []float32) (im_results, im_results) {
    if len(TX_band) != len(TX) {
        log.Printf("%v", fmt.Errorf("Error, TX band list must equal TX freq list"))
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
    // fmt.Println(IM3_full)
    // fmt.Println(IM5_full)

    return im_results{IM3, IM3_full}, im_results{IM5, IM5_full}
}

func CheckRX(rx []float32, rx_band []float32, im_full [][]float32) [][]float32 {
    im_hits := make([][]float32, 0)
    for i := range(rx) {
        rx_min := rx[i] - rx_band[i]/2
        rx_max := rx[i] + rx_band[i]/2
        for im := range(im_full) {
            hits := 0
            pim := []float32{im_full[im][0], im_full[im][1]}
            // Check if edge is inside RX
            if rx_min <= im_full[im][0] && im_full[im][0] <= rx_max {
                hits++
            }
            if rx_min <= im_full[im][1] && im_full[im][1] <= rx_max {
                hits++
            }
            // Check if PIM edge is outside of RX but fully covering it
            if im_full[im][0] <= rx_min && im_full[im][1] >= rx_max {
                hits++
            }

            if hits > 0 {
                im_hits = append(im_hits, []float32{rx[i], pim[0], pim[1]})
            }
        }
    }
    return im_hits
}

func PIM_Calculator() {
    main()
}

func main() {
    print_div("-", 80)
    fmt.Println("|\tThis is PIM Calculator")
    print_div("-", 80)
    // args := os.Args[1:]
    args_TX, args_RX := read_args()

    im3, im5 := Calculate(args_TX.freq, args_TX.band)

    fmt.Println("I've got this IM3:\n", im3)
    print_div("-", 80)
    fmt.Println("I've got this IM5:\n", im5)
    print_div("-", 80)

    im_results := CheckRX(args_RX.freq, args_RX.band, im3.IM_full)
    fmt.Println("------------IM3------------")
    for i:= range(im_results) {
        fmt.Printf("%f is affected by %f\n", im_results[i][0], im_results[i][1:])
    }
    print_div("-", 80)
    fmt.Println("------------IM5------------")
    im_results = CheckRX(args_RX.freq, args_RX.band, im5.IM_full)
    for i:= range(im_results) {
        fmt.Printf("%f is affected by %f\n", im_results[i][0], im_results[i][1:])
    }
}
