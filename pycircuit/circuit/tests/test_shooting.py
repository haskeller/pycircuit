from nose.tools import *
from pycircuit.circuit import *
from pycircuit.circuit.shooting import *
from pycircuit.post import astable, plotall, Waveform, average, db20
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal
from copy import copy
import pylab
from myCap import myC

def test_shooting():
    cir = SubCircuit()
    
    N = 10
    period = 1e-3

    cir['vs'] = VSin(1,gnd, vac=2.0, va=2.0, freq=1/period, phase=20)
    cir['R'] = R(1,2, r=1e4)
    cir['C'] = C(2,gnd, c=1e-8)
    
    ac = PSS(cir)
    resac = AC(cir).solve(1/period)

    pss = PSS(cir)

    res = pss.solve(period=period, timestep = period/N)
    
    v2ac = resac.v(2,gnd)
    v2pss = res['tpss'].v(2,gnd)
    
    t,dt = numeric.linspace(0,period,num=N,endpoint=True,
                            retstep=True)

    v2ref = numeric.imag(v2ac * numeric.exp(2j*numeric.pi*1/period*t))

    w2ref = Waveform(t,v2ref,ylabel='reference', yunit='V', 
                     xunits=('s',), xlabels=('vref(2,gnd!)',))
    
#    print v2pss.astable
#    plotall(v2pss,w2ref)
#    pylab.grid()
#    pylab.show()

    ## Check amplitude error
    v2rms_ac = abs(v2ac) / np.sqrt(2)
    v2rms_pss = abs(res['fpss'].v(2,gnd)).value(1/period)
    assert_almost_equal(v2rms_ac, v2rms_pss)
 
    ## Check error of waveform
    rmserror = numeric.sqrt(average((v2pss-w2ref)**2))
    assert rmserror < 1e-3, 'rmserror=%f too high'%rmserror

 
def test_PSS_nonlinear_C():
    """Test of PSS simulation of RLC-circuit,
    with nonlinear capacitor.
    """
    c = SubCircuit()

    c['VSin'] = VSin(gnd, 1, va=10, freq=50e3)
    c['R1'] = R(1, 2, r=1e6)
    c['C'] = myC(2, gnd)
    #c['L'] = L(2,gnd, L=1e-3)
    pss = PSS(c)
    res = pss.solve(period=1/50e3,timestep=1e-8)
    db20(res['fpss'].v(2)).stem()
    pylab.show()
    plotall(res['tpss'].v(1),res['tpss'].v(2))
    pylab.show()


