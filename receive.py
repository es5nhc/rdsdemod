#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Mon Aug 22 20:17:02 2016
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr
import time


class top_block(gr.top_block):

    def __init__(self, duration=15, gain=20, hpfcutoff=57585, hpfwidth=1370, lpfcutoff=2240, lpfwidth=1075, qrg=106.1, xlatlpfcutoff=80000, xlatlpfwidth=50000):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Parameters
        ##################################################
        self.duration = duration
        self.gain = gain
        self.hpfcutoff = hpfcutoff
        self.hpfwidth = hpfwidth
        self.lpfcutoff = lpfcutoff
        self.lpfwidth = lpfwidth
        self.qrg = qrg
        self.xlatlpfcutoff = xlatlpfcutoff
        self.xlatlpfwidth = xlatlpfwidth

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 47500

        ##################################################
        # Blocks
        ##################################################
        self.rtlsdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.rtlsdr_source_0.set_sample_rate(1e6)
        self.rtlsdr_source_0.set_center_freq(qrg*1e6-150e3, 0)
        self.rtlsdr_source_0.set_freq_corr(45, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(2, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(True, 0)
        self.rtlsdr_source_0.set_gain(gain, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna("", 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
          
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=475,
                decimation=1250,
                taps=None,
                fractional_bw=None,
        )
        self.low_pass_filter_1 = filter.fir_filter_ccf(1, firdes.low_pass(
        	400, 125e3, lpfcutoff, lpfwidth, firdes.WIN_RECTANGULAR, 6.76))
        self.high_pass_filter_0 = filter.fir_filter_fff(1, firdes.high_pass(
        	1, 125e3, hpfcutoff, hpfwidth, firdes.WIN_RECTANGULAR, 6.76))
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(2, (firdes.low_pass(2,1e6,xlatlpfcutoff,xlatlpfwidth,firdes.WIN_RECTANGULAR)), 150e3, 1e6)
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink("waveform.wav", 2, samp_rate, 16)
        self.blocks_multiply_xx_1 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)
        self.blocks_head_0 = blocks.head(gr.sizeof_gr_complex*1, int(samp_rate*(duration+1)))
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=500e3,
        	audio_decimation=4,
        )
        self.analog_sig_source_x_1 = analog.sig_source_f(125e6, analog.GR_SIN_WAVE, 57e6, 1, 0)
        self.analog_sig_source_x_0 = analog.sig_source_f(125e3, analog.GR_COS_WAVE, 57000, 1, 0)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))    
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_multiply_xx_1, 1))    
        self.connect((self.analog_wfm_rcv_0, 0), (self.high_pass_filter_0, 0))    
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_wavfile_sink_0, 1))    
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_wavfile_sink_0, 0))    
        self.connect((self.blocks_float_to_complex_0, 0), (self.low_pass_filter_1, 0))    
        self.connect((self.blocks_head_0, 0), (self.blocks_complex_to_float_0, 0))    
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_float_to_complex_0, 1))    
        self.connect((self.blocks_multiply_xx_1, 0), (self.blocks_float_to_complex_0, 0))    
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_wfm_rcv_0, 0))    
        self.connect((self.high_pass_filter_0, 0), (self.blocks_multiply_xx_0, 0))    
        self.connect((self.high_pass_filter_0, 0), (self.blocks_multiply_xx_1, 0))    
        self.connect((self.low_pass_filter_1, 0), (self.rational_resampler_xxx_0, 0))    
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_head_0, 0))    
        self.connect((self.rtlsdr_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))    

    def get_duration(self):
        return self.duration

    def set_duration(self, duration):
        self.duration = duration
        self.blocks_head_0.set_length(int(self.samp_rate*(self.duration+1)))

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.rtlsdr_source_0.set_gain(self.gain, 0)

    def get_hpfcutoff(self):
        return self.hpfcutoff

    def set_hpfcutoff(self, hpfcutoff):
        self.hpfcutoff = hpfcutoff
        self.high_pass_filter_0.set_taps(firdes.high_pass(1, 125e3, self.hpfcutoff, self.hpfwidth, firdes.WIN_RECTANGULAR, 6.76))

    def get_hpfwidth(self):
        return self.hpfwidth

    def set_hpfwidth(self, hpfwidth):
        self.hpfwidth = hpfwidth
        self.high_pass_filter_0.set_taps(firdes.high_pass(1, 125e3, self.hpfcutoff, self.hpfwidth, firdes.WIN_RECTANGULAR, 6.76))

    def get_lpfcutoff(self):
        return self.lpfcutoff

    def set_lpfcutoff(self, lpfcutoff):
        self.lpfcutoff = lpfcutoff
        self.low_pass_filter_1.set_taps(firdes.low_pass(400, 125e3, self.lpfcutoff, self.lpfwidth, firdes.WIN_RECTANGULAR, 6.76))

    def get_lpfwidth(self):
        return self.lpfwidth

    def set_lpfwidth(self, lpfwidth):
        self.lpfwidth = lpfwidth
        self.low_pass_filter_1.set_taps(firdes.low_pass(400, 125e3, self.lpfcutoff, self.lpfwidth, firdes.WIN_RECTANGULAR, 6.76))

    def get_qrg(self):
        return self.qrg

    def set_qrg(self, qrg):
        self.qrg = qrg
        self.rtlsdr_source_0.set_center_freq(self.qrg*1e6-150e3, 0)

    def get_xlatlpfcutoff(self):
        return self.xlatlpfcutoff

    def set_xlatlpfcutoff(self, xlatlpfcutoff):
        self.xlatlpfcutoff = xlatlpfcutoff
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.low_pass(2,1e6,self.xlatlpfcutoff,self.xlatlpfwidth,firdes.WIN_RECTANGULAR)))

    def get_xlatlpfwidth(self):
        return self.xlatlpfwidth

    def set_xlatlpfwidth(self, xlatlpfwidth):
        self.xlatlpfwidth = xlatlpfwidth
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.low_pass(2,1e6,self.xlatlpfcutoff,self.xlatlpfwidth,firdes.WIN_RECTANGULAR)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_head_0.set_length(int(self.samp_rate*(self.duration+1)))


def argument_parser():
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option(
        "-t", "--duration", dest="duration", type="eng_float", default=eng_notation.num_to_str(15),
        help="Set capture duration in seconds [default=%default]")
    parser.add_option(
        "-g", "--gain", dest="gain", type="eng_float", default=eng_notation.num_to_str(20),
        help="Set RF gain [default=%default]")
    parser.add_option(
        "", "--hpfcutoff", dest="hpfcutoff", type="intx", default=57585,
        help="Set cutoff frequency of HPF after WFM demodulation [default=%default]")
    parser.add_option(
        "", "--hpfwidth", dest="hpfwidth", type="intx", default=1370,
        help="Set transition width of HPF after WFM demodulation [default=%default]")
    parser.add_option(
        "", "--lpfcutoff", dest="lpfcutoff", type="intx", default=2240,
        help="Set cutoff frequency of LPF processing the RDS symbols [default=%default]")
    parser.add_option(
        "", "--lpfwidth", dest="lpfwidth", type="intx", default=1075,
        help="Set transition width of LPF processing the RDS symbols [default=%default]")
    parser.add_option(
        "-f", "--qrg", dest="qrg", type="eng_float", default=eng_notation.num_to_str(106.1),
        help="Set frequency [default=%default]")
    parser.add_option(
        "", "--xlatlpfcutoff", dest="xlatlpfcutoff", type="intx", default=80000,
        help="Set cutoff frequency of the LPF tapped to Frequency Xlating filter before WFM demod [default=%default]")
    parser.add_option(
        "", "--xlatlpfwidth", dest="xlatlpfwidth", type="intx", default=50000,
        help="Set transition width of the LPF tapped to Frequency Xlating filter before WFM demod [default=%default]")
    return parser


def main(top_block_cls=top_block, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(duration=options.duration, gain=options.gain, hpfcutoff=options.hpfcutoff, hpfwidth=options.hpfwidth, lpfcutoff=options.lpfcutoff, lpfwidth=options.lpfwidth, qrg=options.qrg, xlatlpfcutoff=options.xlatlpfcutoff, xlatlpfwidth=options.xlatlpfwidth)
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
