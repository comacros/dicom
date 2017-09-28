import struct

class bmp8bit:
    def __init__(self, width, height, depth, pixeldata):
        if depth not in [8]:
            raise ValueError('dept must be 8')
        self.pixeldata = list(pixeldata)
        self.width = width
        self.height = height
        self.depth = depth
        for i in range(int(self.height/2)):
            A = self.pixeldata[i * self.width : (i + 1) * self.width]
            B = self.pixeldata[(self.height - i - 1) * self.width : (self.height - i) * self.width]
            self.pixeldata[i * self.width : (i+1) * self.width] = B
            self.pixeldata[(self.height - i - 1) * self.width : (self.height - i) * self.width] = A

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            # FILE header
            f.write(b'BM')
            f.write(struct.pack('I', int(14 + 40 + (1 << self.depth) * 4 + self.width * self.height * self.depth / 8)))
            f.write(b'\x00\x00\x00\x00')
            f.write(struct.pack('I', int(14 + 40 + (1 << self.depth) * 4)))

            # DIB header
            f.write(struct.pack('I', 40))   # DIB header size
            f.write(struct.pack('2i', self.width, self.height))
            f.write(b'\x01\x00')            # color plane, must be 1
            f.write(struct.pack('h', self.depth))   # bits per pixel
            f.write(struct.pack('i', 0))    # compression, 0 = RGB
            f.write(struct.pack('i', int(self.width * self.height * self.depth / 8)))    # image size
            f.write(struct.pack('2i', 5669, 5669))  # X/Y Pixels Per Meter
            f.write(struct.pack('i', 1 << self.depth))  # Colors in Color Table
            f.write(struct.pack('i', 0))   # Important Color Count
            for i in range(1 << self.depth):
                f.write(struct.pack('4B', i, i, i, 0))
            pixels = struct.pack('{0:d}B'.format(self.width * self.height), *self.pixeldata)
            f.write(pixels)



if __name__ == '__main__':
    pass