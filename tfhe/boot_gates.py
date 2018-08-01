import time

from .numeric_functions import modSwitchToTorus32
from .lwe import (
    LweSampleArray,
    lweKeySwitch,
    )
from .lwe import (
    lweAddTo_gpu,
    lweSubTo_gpu,
    lweAddMulTo_gpu,
    lweSubMulTo_gpu,
    lweNoiselessTrivial_gpu,
    lweNegate_gpu,
    lweCopy_gpu,
    )
from .keys import TFHECloudKey
from .lwe_bootstrapping import bootstrap
from .performance import performance_parameters

from . import lwe_bootstrapping

#*#*****************************************
# zones on the torus -> to see
#*#*****************************************


def result_shape(shape1, shape2):
    if len(shape1) > len(shape2):
        shape2 = (1,) * (len(shape1) - len(shape2)) + shape2
    else:
        shape1 = (1,) * (len(shape2) - len(shape1)) + shape1

    if any((l1 != l2 and l1 > 1 and l2 > 1) for l1, l2 in zip(shape1, shape2)):
        raise ValueError("Incompatible shapes: {s1}, {s2}".format(s1=shape1, s2=shape2))

    return tuple((l1 if l1 > 1 else l2) for l1, l2 in zip(shape1, shape2))


"""
 * Homomorphic bootstrapped NAND gate
 * Takes in input 2 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE bootstrapped sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_NAND_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray, cb: LweSampleArray,
        perf_params=None):

    if perf_params is None:
        perf_params = performance_parameters(tfhe_params=bk.params)

    rshape = result_shape(ca.shape_info.shape, cb.shape_info.shape)
    assert rshape == result.shape_info.shape

    in_out_params = bk.params.in_out_params

    t = time.time()
    temp_result = LweSampleArray.empty(thr, in_out_params, rshape)
    thr.synchronize()
    lwe_bootstrapping.to_gpu_time += time.time() - t

    #compute: (0,1/8) - ca - cb
    NandConst = modSwitchToTorus32(1, 8)
    lweNoiselessTrivial_gpu(thr, temp_result, NandConst)
    lweSubTo_gpu(thr, temp_result, ca)
    lweSubTo_gpu(thr, temp_result, cb)

    #if the phase is positive, the result is 1/8
    #if the phase is positive, else the result is -1/8
    MU = modSwitchToTorus32(1, 8)
    bootstrap(thr, result, bk.bkFFT, MU, temp_result, perf_params)


"""
 * Homomorphic bootstrapped OR gate
 * Takes in input 2 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE bootstrapped sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_OR_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray, cb: LweSampleArray,
        perf_params=None):

    if perf_params is None:
        perf_params = performance_parameters(tfhe_params=bk.params)

    rshape = result_shape(ca.shape_info.shape, cb.shape_info.shape)
    assert rshape == result.shape_info.shape

    in_out_params = bk.params.in_out_params
    temp_result = LweSampleArray.empty(thr, in_out_params, result.shape_info.shape)

    #compute: (0,1/8) + ca + cb
    OrConst = modSwitchToTorus32(1, 8)
    lweNoiselessTrivial_gpu(thr, temp_result, OrConst)
    lweAddTo_gpu(thr, temp_result, ca)
    lweAddTo_gpu(thr, temp_result, cb)

    #if the phase is positive, the result is 1/8
    #if the phase is positive, else the result is -1/8
    MU = modSwitchToTorus32(1, 8)
    bootstrap(thr, result, bk.bkFFT, MU, temp_result, perf_params)


"""
 * Homomorphic bootstrapped AND gate
 * Takes in input 2 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE bootstrapped sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_AND_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray, cb: LweSampleArray,
        perf_params=None):

    if perf_params is None:
        perf_params = performance_parameters(tfhe_params=bk.params)

    rshape = result_shape(ca.shape_info.shape, cb.shape_info.shape)
    assert rshape == result.shape_info.shape

    in_out_params = bk.params.in_out_params
    temp_result = LweSampleArray.empty(thr, in_out_params, result.shape_info.shape)

    #compute: (0,-1/8) + ca + cb
    AndConst = modSwitchToTorus32(-1, 8)
    lweNoiselessTrivial_gpu(thr, temp_result, AndConst)
    lweAddTo_gpu(thr, temp_result, ca)
    lweAddTo_gpu(thr, temp_result, cb)

    #if the phase is positive, the result is 1/8
    #if the phase is positive, else the result is -1/8
    MU = modSwitchToTorus32(1, 8)
    bootstrap(thr, result, bk.bkFFT, MU, temp_result, perf_params)


"""
 * Homomorphic bootstrapped XOR gate
 * Takes in input 2 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE bootstrapped sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_XOR_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray, cb: LweSampleArray,
        perf_params=None):

    if perf_params is None:
        perf_params = performance_parameters(tfhe_params=bk.params)

    rshape = result_shape(ca.shape_info.shape, cb.shape_info.shape)
    assert rshape == result.shape_info.shape

    in_out_params = bk.params.in_out_params
    temp_result = LweSampleArray.empty(thr, in_out_params, result.shape_info.shape)

    #compute: (0,1/4) + 2*(ca + cb)
    XorConst = modSwitchToTorus32(1, 4)
    lweNoiselessTrivial_gpu(thr, temp_result, XorConst)
    lweAddMulTo_gpu(thr, temp_result, 2, ca)
    lweAddMulTo_gpu(thr, temp_result, 2, cb)

    #if the phase is positive, the result is 1/8
    #if the phase is positive, else the result is -1/8
    MU = modSwitchToTorus32(1, 8)
    bootstrap(thr, result, bk.bkFFT, MU, temp_result, perf_params)


"""
 * Homomorphic bootstrapped XNOR gate
 * Takes in input 2 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE bootstrapped sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_XNOR_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray, cb: LweSampleArray,
        perf_params=None):

    if perf_params is None:
        perf_params = performance_parameters(tfhe_params=bk.params)

    rshape = result_shape(ca.shape_info.shape, cb.shape_info.shape)
    assert rshape == result.shape_info.shape

    in_out_params = bk.params.in_out_params
    temp_result = LweSampleArray.empty(thr, in_out_params, result.shape_info.shape)

    #compute: (0,-1/4) + 2*(-ca-cb)
    XnorConst = modSwitchToTorus32(-1, 4)
    lweNoiselessTrivial_gpu(thr, temp_result, XnorConst)
    lweSubMulTo_gpu(thr, temp_result, 2, ca)
    lweSubMulTo_gpu(thr, temp_result, 2, cb)

    #if the phase is positive, the result is 1/8
    #if the phase is positive, else the result is -1/8
    MU = modSwitchToTorus32(1, 8)
    bootstrap(thr, result, bk.bkFFT, MU, temp_result, perf_params)


"""
 * Homomorphic bootstrapped NOT gate (doesn't need to be bootstrapped)
 * Takes in input 1 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_NOT_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray,
        perf_params=None):
    in_out_params = bk.params.in_out_params
    lweNegate_gpu(thr, result, ca)


"""
 * Homomorphic bootstrapped COPY gate (doesn't need to be bootstrapped)
 * Takes in input 1 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_COPY_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray,
        perf_params=None):
    in_out_params = bk.params.in_out_params
    lweCopy_gpu(thr, result, ca)


"""
 * Homomorphic Trivial Constant gate (doesn't need to be bootstrapped)
 * Takes a boolean value)
 * Outputs a LWE sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_CONSTANT_(thr, bk: TFHECloudKey, result: LweSampleArray, val):
    in_out_params = bk.params.in_out_params
    MU = modSwitchToTorus32(1, 8)
    lweNoiselessTrivial_gpu(thr, result, MU if val else -MU)


"""
 * Homomorphic bootstrapped NOR gate
 * Takes in input 2 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE bootstrapped sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_NOR_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray, cb: LweSampleArray,
        perf_params=None):

    if perf_params is None:
        perf_params = performance_parameters(tfhe_params=bk.params)

    rshape = result_shape(ca.shape_info.shape, cb.shape_info.shape)
    assert rshape == result.shape_info.shape

    in_out_params = bk.params.in_out_params
    temp_result = LweSampleArray.empty(thr, in_out_params, result.shape_info.shape)

    #compute: (0,-1/8) - ca - cb
    NorConst = modSwitchToTorus32(-1, 8)
    lweNoiselessTrivial_gpu(thr, temp_result, NorConst)
    lweSubTo_gpu(thr, temp_result, ca)
    lweSubTo_gpu(thr, temp_result, cb)

    #if the phase is positive, the result is 1/8
    #if the phase is positive, else the result is -1/8
    MU = modSwitchToTorus32(1, 8)
    bootstrap(thr, result, bk.bkFFT, MU, temp_result, perf_params)


"""
 * Homomorphic bootstrapped AndNY Gate: not(a) and b
 * Takes in input 2 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE bootstrapped sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_ANDNY_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray, cb: LweSampleArray,
        perf_params=None):

    if perf_params is None:
        perf_params = performance_parameters(tfhe_params=bk.params)

    rshape = result_shape(ca.shape_info.shape, cb.shape_info.shape)
    assert rshape == result.shape_info.shape

    in_out_params = bk.params.in_out_params
    temp_result = LweSampleArray.empty(thr, in_out_params, result.shape_info.shape)

    #compute: (0,-1/8) - ca + cb
    AndNYConst = modSwitchToTorus32(-1, 8)
    lweNoiselessTrivial_gpu(thr, temp_result, AndNYConst)
    lweSubTo_gpu(thr, temp_result, ca)
    lweAddTo_gpu(thr, temp_result, cb)

    #if the phase is positive, the result is 1/8
    #if the phase is positive, else the result is -1/8
    MU = modSwitchToTorus32(1, 8)
    bootstrap(thr, result, bk.bkFFT, MU, temp_result, perf_params)


"""
 * Homomorphic bootstrapped AndYN Gate: a and not(b)
 * Takes in input 2 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE bootstrapped sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_ANDYN_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray, cb: LweSampleArray,
        perf_params=None):

    if perf_params is None:
        perf_params = performance_parameters(tfhe_params=bk.params)

    rshape = result_shape(ca.shape_info.shape, cb.shape_info.shape)
    assert rshape == result.shape_info.shape

    in_out_params = bk.params.in_out_params
    temp_result = LweSampleArray.empty(thr, in_out_params, result.shape_info.shape)

    #compute: (0,-1/8) + ca - cb
    AndYNConst = modSwitchToTorus32(-1, 8)
    lweNoiselessTrivial_gpu(thr, temp_result, AndYNConst)
    lweAddTo_gpu(thr, temp_result, ca)
    lweSubTo_gpu(thr, temp_result, cb)

    #if the phase is positive, the result is 1/8
    #if the phase is positive, else the result is -1/8
    MU = modSwitchToTorus32(1, 8)
    bootstrap(thr, result, bk.bkFFT, MU, temp_result, perf_params)


"""
 * Homomorphic bootstrapped OrNY Gate: not(a) or b
 * Takes in input 2 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE bootstrapped sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_ORNY_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray, cb: LweSampleArray,
        perf_params=None):

    if perf_params is None:
        perf_params = performance_parameters(tfhe_params=bk.params)

    rshape = result_shape(ca.shape_info.shape, cb.shape_info.shape)
    assert rshape == result.shape_info.shape

    in_out_params = bk.params.in_out_params
    temp_result = LweSampleArray.empty(thr, in_out_params, result.shape_info.shape)

    #compute: (0,1/8) - ca + cb
    OrNYConst = modSwitchToTorus32(1, 8)
    lweNoiselessTrivial_gpu(thr, temp_result, OrNYConst)
    lweSubTo_gpu(thr, temp_result, ca)
    lweAddTo_gpu(thr, temp_result, cb)

    #if the phase is positive, the result is 1/8
    #if the phase is positive, else the result is -1/8
    MU = modSwitchToTorus32(1, 8)
    bootstrap(thr, result, bk.bkFFT, MU, temp_result, perf_params)


"""
 * Homomorphic bootstrapped OrYN Gate: a or not(b)
 * Takes in input 2 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE bootstrapped sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_ORYN_(
        thr, bk: TFHECloudKey, result: LweSampleArray, ca: LweSampleArray, cb: LweSampleArray,
        perf_params=None):

    if perf_params is None:
        perf_params = performance_parameters(tfhe_params=bk.params)

    rshape = result_shape(ca.shape_info.shape, cb.shape_info.shape)
    assert rshape == result.shape_info.shape

    in_out_params = bk.params.in_out_params
    temp_result = LweSampleArray.empty(thr, in_out_params, result.shape_info.shape)

    #compute: (0,1/8) + ca - cb
    OrYNConst = modSwitchToTorus32(1, 8)
    lweNoiselessTrivial_gpu(thr, temp_result, OrYNConst)
    lweAddTo_gpu(thr, temp_result, ca)
    lweSubTo_gpu(thr, temp_result, cb)

    #if the phase is positive, the result is 1/8
    #if the phase is positive, else the result is -1/8
    MU = modSwitchToTorus32(1, 8)
    bootstrap(thr, result, bk.bkFFT, MU, temp_result, perf_params)


"""
 * Homomorphic bootstrapped Mux(a,b,c) = a?b:c = a*b + not(a)*c
 * Takes in input 3 LWE samples (with message space [-1/8,1/8], noise<1/16)
 * Outputs a LWE bootstrapped sample (with message space [-1/8,1/8], noise<1/16)
"""
def tfhe_gate_MUX_(
        thr,
        bk: TFHECloudKey, result: LweSampleArray,
        a: LweSampleArray, b: LweSampleArray, c: LweSampleArray,
        perf_params=None):

    if perf_params is None:
        perf_params = performance_parameters(tfhe_params=bk.params)

    rshape = result_shape(a.shape_info.shape, result_shape(b.shape_info.shape, c.shape_info.shape))
    assert rshape == result.shape_info.shape

    MU = modSwitchToTorus32(1, 8)
    in_out_params = bk.params.in_out_params
    extracted_params = bk.params.tgsw_params.tlwe_params.extracted_lweparams

    temp_result = LweSampleArray.empty(thr, in_out_params, result.shape_info.shape)
    temp_result1 = LweSampleArray.empty(thr, extracted_params, result.shape_info.shape)
    u1 = LweSampleArray.empty(thr, extracted_params, result.shape_info.shape)
    u2 = LweSampleArray.empty(thr, extracted_params, result.shape_info.shape)

    #compute "AND(a,b)": (0,-1/8) + a + b
    AndConst = modSwitchToTorus32(-1, 8)
    lweNoiselessTrivial_gpu(thr, temp_result, AndConst)
    lweAddTo_gpu(thr, temp_result, a)
    lweAddTo_gpu(thr, temp_result, b)
    # Bootstrap without KeySwitch
    bootstrap(thr, u1, bk.bkFFT, MU, temp_result, perf_params, no_keyswitch=True)

    #compute "AND(not(a),c)": (0,-1/8) - a + c
    lweNoiselessTrivial_gpu(thr, temp_result, AndConst)
    lweSubTo_gpu(thr, temp_result, a)
    lweAddTo_gpu(thr, temp_result, c)
    # Bootstrap without KeySwitch
    bootstrap(thr, u2, bk.bkFFT, MU, temp_result, perf_params, no_keyswitch=True)

    # Add u1=u1+u2
    MuxConst = modSwitchToTorus32(1, 8)
    lweNoiselessTrivial_gpu(thr, temp_result1, MuxConst)
    lweAddTo_gpu(thr, temp_result1, u1)
    lweAddTo_gpu(thr, temp_result1, u2)

    # Key switching
    lweKeySwitch(thr, result, bk.bkFFT.ks, temp_result1)
