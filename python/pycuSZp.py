import ctypes
import numpy as np

# Load the shared library (using default installation path, replace if neccessary)
lib = ctypes.CDLL('../install/lib/libcuSZp.so')

# Define ctypes for the C functions with void pointers for flexible input/output data
lib.cuSZp_compress.argtypes = [
    ctypes.c_void_p,  # GPU pointer for input data (void* for flexibility)
    ctypes.c_void_p,  # GPU pointer for compressed output (interpreted as unsigned char*)
    ctypes.c_size_t,  # Number of elements
    ctypes.POINTER(ctypes.c_size_t),  # Compressed size output
    ctypes.c_float,  # Error bound
    ctypes.c_int,    # Data type (0 for float, 1 for double)
    ctypes.c_int,    # Mode (0 for plain, 1 for outlier)
    ctypes.c_void_p  # Stream (optional, can be None)
]

lib.cuSZp_decompress.argtypes = [
    ctypes.c_void_p,  # GPU pointer for decompressed output (void*)
    ctypes.c_void_p,  # Compressed input buffer (unsigned char*)
    ctypes.c_size_t,  # Number of elements
    ctypes.c_size_t,  # Compressed size
    ctypes.c_float,   # Error bound
    ctypes.c_int,     # Data type (0 for float, 1 for double)
    ctypes.c_int,     # Mode (0 for plain, 1 for outlier)
    ctypes.c_void_p   # Stream (optional, can be None)
]

lib.cuSZp_fixed_ratio.argtypes = [
    ctypes.c_void_p,                       # d_oriData (void*)
    ctypes.c_void_p,                       # d_cmpBytes (unsigned char*)
    ctypes.c_size_t,                       # nbEle
    ctypes.POINTER(ctypes.c_size_t),       # *cmpSize
    ctypes.c_float,                        # range = max(x) - min(x) on host
    ctypes.c_int,                          # sample_rate
    ctypes.c_float,                        # ratio (target compression ratio)
    ctypes.c_void_p,                       # stream (None for default)
]
lib.cuSZp_fixed_ratio.restype = None



class cuSZp:
    def __init__(self):
        pass

    def compress(self, d_oriData, d_cmpBytes, num_elements, error_bound=0.01, data_type=0, mode=0):
        # Initialize size for compressed data
        compressed_size = ctypes.c_size_t(0)

        # Call the C function
        lib.cuSZp_compress(
            d_oriData,  # GPU pointer for input data
            d_cmpBytes,  # GPU pointer for compressed output (unsigned char*)
            num_elements,
            ctypes.byref(compressed_size),
            ctypes.c_float(error_bound),
            ctypes.c_int(data_type),
            ctypes.c_int(mode),
            None  # Stream (optional, set to None)
        )
        
        return compressed_size.value

    def decompress(self, d_decData, d_cmpBytes, num_elements, compressed_size, error_bound=0.01, data_type=0, mode=0):
        # Call the C function
        lib.cuSZp_decompress(
            d_decData,  # GPU pointer for decompressed output
            d_cmpBytes,  # GPU pointer for compressed input
            num_elements,
            compressed_size,
            ctypes.c_float(error_bound),
            ctypes.c_int(data_type),
            ctypes.c_int(mode),
            None  # Stream (optional, set to None)
        )
    def compress_fixed_ratio(self, d_oriData, d_cmpBytes, num_elements,
                             data_range, sample_rate=1000, ratio=4.0):
                             
        compressed_size = ctypes.c_size_t(0)
        lib.cuSZp_fixed_ratio(
            d_oriData,
            d_cmpBytes,
            ctypes.c_size_t(num_elements),
            ctypes.byref(compressed_size),
            ctypes.c_float(data_range),
            ctypes.c_int(sample_rate),
            ctypes.c_float(ratio),
            None
        )
        return compressed_size.value
