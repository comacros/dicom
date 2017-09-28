'''
DCMtransfersyntax is a dictionary of {'Value':(explicitVR, littleEndian)}.
'''

DCMtransfersyntax = {
    '1.2.840.10008.1.2': (False, True),         # Native: implicit VR, little endian
    '1.2.840.10008.1.2.1': (True, True),        # Native: explicit VR, little endian
    '1.2.840.10008.1.2.2': (True, False),       # Native: explicit VR, bit endian

    # '1.2.840.10008.1.2.5': (True, True),        # RLE
    #
    # '1.2.840.10008.1.2.4.50': (True, True),     # Lossy JPEG Compression, 8-bit
    # '1.2.840.10008.1.2.4.57': (True, True),     # JPEG Lossless, Non-Hierarchical (Process 14)
    # '1.2.840.10008.1.2.4.70': (True, True),     # JPEG Lossless, Non-Hierarchical,
    #                                             #   First-OrderPrediction (Process 14 [Selection Value 1]):
    #                                             #   Default Transfer Syntax for Lossless JPEGImage Compression
}