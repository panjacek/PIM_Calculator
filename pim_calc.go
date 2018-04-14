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
    TX []float32
    TX_band []float32
}

// divider print
func print_div(character string, num int) {
    for e:=0; e < num; e++ {
        fmt.Print(character)
    }
    fmt.Print("\n")
}

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
func read_args() (config) {
    args_len := len(os.Args)
    TX := os.Args[1]
    var TX_band string
    if args_len >= 3 {
        TX_band = os.Args[2]
    }

    // calc_config := config(convert_arg(TX), convert_arg(TX_band))
    TX_new := convert_arg(TX)
    TX_new_band := convert_arg(TX_band)

    return config{TX_new, TX_new_band}
    // return calc_config
}


func get_im3(tx1 float32, tx2 float32, tx3 float32) (float32) {
    return tx1 + tx2 - tx3
}

func get_im5(tx1 float32, tx2 float32, tx3 float32, tx4 float32, tx5 float32) (float32) {
    return tx1 + tx2 + tx3 - tx4 - tx5
}

func remove_duplicates(im_array []float32) (string){
    // TODO:
    return ""
}

func calculate(TX []float32, TX_band []float32) (string) {
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

    im3_len := len(IM3)
    IM3_full := make([][]float32, 0)
    im5_len := len(IM5)
    IM5_full := make([][]float32, 0)

    // IM f0 - band, f0 + band
    for i := 0; i < im5_len; i++ {
        if i < im3_len {
            im_tmp := [][]float32{{IM3[i] - IM3_band[i]/2.0, IM3[i] + IM3_band[i]/2.0}}
            // fmt.Println(im_tmp)
            IM3_full = append(IM3_full, im_tmp...)
        }
        if max_order == 5 {
            im_tmp := [][]float32{{IM5[i] - IM5_band[i]/2.0, IM5[i] + IM5_band[i]/2.0}}
            IM5_full = append(IM5_full, im_tmp...)
        }
    }
    print_div("-", 80)
    fmt.Println(IM3_full)
    fmt.Println(IM5_full)

    // clean the duplicates
    return ""
}

func testme() {
    TX := []float32{1980, 1940}
    TX_band := []float32{5, 5}
    result := calculate(TX, TX_band)

    fmt.Println("I've got this:\n", result)
}

func main() {
    print_div("-", 80)
    fmt.Println("|\tThis is PIMC calc")
    print_div("-", 80)
    args := os.Args[1:]

    if len(args) < 2 {
        log.Printf("%v", fmt.Errorf("I need at least TX list"))
        fmt.Println("Unit Tests")
        testme()
    } else {
        args := read_args()
        calculate(args.TX, args.TX_band)
    }
}
