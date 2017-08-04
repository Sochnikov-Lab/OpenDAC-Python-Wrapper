# Acquisition Widgets
Acquire:
  Ch Select:        "cba_ch#" where # = 0 to 3
  Samples:          "lea_samples"
  Sample Rate:      "lea_srate"
  Integration Time: "lea_inttime"
  Start:            "butta_start"
Ramp & Read:
  ADC Ch Select:    "cbri_ch#" where # = 0 to 3
  Start:            "buttrr_start"
Data:
  Save CSV:         "butts_csv"
  Plot:             "butts_plot"
  ResetDAC:         "butts_reset"
  ClearBuffer:      "butts_clear"

# Output Widgets:
DC:
  Set Channel:      "buttset_ch#" where # = 0 to 3
    --To val from:  "leset_ch#" where # = 0 to 3
  Set All:          "buttset_all"
  Set All to 0V:    "buttset_0v"
Sine:
  Enable output:    "cbsin_ch#" where # = 0 to 3
  DC Offset:        "lesin_off_ch#" where # = 0 to 3
  Amplitude:        "lesin_amp_ch#" where # = 0 to 3
  Frequency:        "lesin_freq_ch#" where # = 0 to 3
  Phase:            "lesin_phi_ch#" where # = 0 to 3
  Duration:         "lesin_duration"
  Start:            "buttsin_start"
Ramp:
  Enable Channel:   "cbro_ch#" where # = 0 to 3
  Init voltage:     "lervi_ch#" where # = 0 to 3
  Final voltage:    "lervf_ch#" where # = 0 to 3
  Steps:            "ler_steps"
  Interval:         "ler_intrv"
  Start:            "buttr_start"

# Status Widgets
  Comport Select:   "coboxsp_prt"
  Baudrate Select:  "lesp_baud"
  Connect:          "buttsp_conn"
  Disconnect:       "buttsp_disconn"
  progbar:          "pbar_task"
