import io
import struct

from attribute import DCMattribute
from transfersyntax import DCMtransfersyntax
import bmp

def DCMcharset(charsets):
    lstCharset = charsets.split('\\')
    while len(lstCharset) < 3:
        lstCharset.append(lstCharset[-1])

    mapCharset = {'': 'latin1',
                  'ISO_IR 100': 'iso_ir_100',
                  'ISO_IR 126': 'iso_ir_126',
                  'ISO_IR 127': 'iso_ir_127',
                  'ISO_IR 144': 'iso_ir_144',
                  'ISO_IR 192': 'utf8',
                  'ISO 2022 IR 13': 'shift_jis',
                  'ISO 2022 IR 87': 'iso2022_jp',
                  'ISO 2022 IR 149': 'euc_kr',
                  'GB18030': 'gb18030'}

    return [mapCharset.get(charset.strip(), 'latin1') for charset in lstCharset]


def DCMvalue(storage, vr, littleEndian=True, encodings=['latin1']):
    if vr in ['AE', 'AS']:
        return storage.val().decode(encodings[0]).strip(' \x00')
    elif vr == 'AT':
        vm = int(storage.length / 4)
        struct_format = '{0}{1:d}H'.format('<' if littleEndian else '>', vm * 2)
        tags = struct.unpack(struct_format, storage[0:4*vm].val())
        attribute_tags = []
        for i in range(vm):
            attribute_tags.append(('%04x' % tags[i * 2], '%04x' % tags[i * 2 + 1]))
        return attribute_tags
    elif vr in ['CS']:
        return storage.val().decode(encodings[0]).strip(' \x00')
    elif vr in ['DA', 'DS', 'DT']:
        return storage.val().decode(encodings[0]).strip(' \x00')
    elif vr == 'FL':
        vm = int(storage.length / 4)
        struct_format = '{0}{1:d}f'.format('<' if littleEndian else '>', vm)
        values = struct.unpack(struct_format, storage[0:4*vm].val())
        return values[0] if vm == 1 else values
    elif vr == 'FD':
        vm = int(storage.length / 8)
        struct_format = '{0}{1:d}d'.format('<' if littleEndian else '>', vm)
        values = struct.unpack(struct_format, storage[0:8*vm].val())
        return values[0] if vm == 1 else values
    elif vr in ['IS', 'LO']:
        return storage.val().decode(encodings[0]).strip('\x00')
    elif vr == 'LT':
        return storage.val().decode(encodings[0]).rstrip(' \x00')
    elif vr == 'OB':
        return struct.unpack('{0}B'.format(int(storage.length)), storage.val())
    elif vr == 'OD':
        vm = int(storage.length / 8)
        struct_format = '{0}{1:d}d'.format('<' if littleEndian else '>', vm)
        return struct.unpack(struct_format, storage[0:8*vm].val())
    elif vr == 'OF':
        vm = int(storage.length / 4)
        struct_format = '{0}{1:d}f'.format('<' if littleEndian else '>', vm)
        return struct.unpack(struct_format, storage[0:4*vm].val())
    elif vr == 'OW':
        vm = int(storage.length / 2)
        struct_format = '{0}{1:d}H'.format('<' if littleEndian else '>', vm)
        return struct.unpack(struct_format, storage[0:2*vm].val())
    elif vr == 'PN':
        names = storage.val().split(b'=')
        pnencodings = encodings
        while len(pnencodings) < len(names):
            pnencodings.append(pnencodings[-1])
        unicodenames = []
        for i in range(len(names)):
            if pnencodings[i] == 'euc_kr':
                latin1name = names[i].decode('latin1').replace('\x1b$)C', '').replace('\x1b(B', '')
                names[i] = latin1name.encode('latin1')
            unicodenames.append(names[i].decode(pnencodings[i]))
        return '='.join(unicodenames)
    elif vr == 'SH':
        return storage.val().decode(encodings[0]).strip('\x00')
    elif vr == 'SL':
        vm = int(storage.length / 4)
        struct_format = '{0}{1:d}i'.format('<' if littleEndian else '>', vm)
        values = struct.unpack(struct_format, storage[0:4*vm].val())
        return values[0] if vm == 1 else values
    elif vr == 'SQ':
        return None
    elif vr == 'SS':
        vm = int(storage.length / 2)
        struct_format = '{0}{1:d}h'.format('<' if littleEndian else '>', vm)
        values = struct.unpack(struct_format, storage[0:2*vm].val())
        return values[0] if vm == 1 else values
    elif vr == 'ST':
        return storage.val().decode(encodings[0])
    elif vr == 'TM':
        return storage.val().decode(encodings[0])
    elif vr == 'UI':
        return storage.val().decode(encodings[0]).strip('\x00')
    elif vr == 'UL':
        vm = int(storage.length / 4)
        struct_format = '{0}{1:d}I'.format('<' if littleEndian else '>', vm)
        values = struct.unpack(struct_format, storage[0:4*vm].val())
        return values[0] if vm == 1 else values
    elif vr == 'US':
        vm = storage.length / 2
        return struct.unpack('<%dH' % vm if littleEndian else '>%dH' % vm, storage.val())
    else:
        return None


class DCMstorage:
    def __init__(self, binary, offset, length = -1):
        if offset < 0:
            raise BufferError('offset = %d < 0' % offset)

        if length > len(binary) - offset:
            raise BufferError('length = %d > %d' % length, len(binary) - offset)

        self.offset = offset
        self.length = len(binary) - offset if length < 0 else length
        self.binary = binary

    def val(self):
        return self.binary[self.offset:self.offset + self.length]

    def __getitem__(self, key):
        if isinstance(key, int):
            if key >= self.length:
                raise BufferError('index >= %d' % self.length)

            return DCMstorage(self.binary, self.offset + key, 1)
        elif isinstance(key, slice):
            if key.step != 1 and key.step is not None:
                raise TypeError('unsupported slice.step')
            if key.start > key.stop:
                raise BufferError('start > stop')
            if key.start < 0 or key.stop < 0:
                raise BufferError('negative index')

            start = key.start + self.offset if key.start < self.length else self.offset + self.length
            stop = key.stop + self.offset if key.stop <= self.length else self.offset + self.length

            return DCMstorage(self.binary, start, stop - start)
        else:
            raise TypeError('unsupported operand type: %s' % type(key).__name__)


class DCMdataset:
    def __init__(self, storage):
        if not isinstance(storage, DCMstorage):
            raise TypeError('unsupported input data of type %s' % type(storage).__name__)

        self.storage = storage
        self.elements = []

        self.explicitVR = False
        self.littleEndian = True

        explicitVR = True
        littleEndian = True
        metalength = None
        charsets = ['latin1']
        metagroup = True
        while len(self.storage.binary) > self.storage.offset:
            element = DCMelement(self.storage, explicitVR, littleEndian, charsets)

            if element is None:
                break
            print(element)
            self.elements.append(element)
            if element.GroupNumber == 0x0002:
                if element.ElementNumber == 0x0010:
                    try:
                        self.explicitVR, self.littleEndian = DCMtransfersyntax[element.value]
                    except KeyError:
                        # PS.5:A.4 Transfer Syntaxes For Encapsulation oe Encoded Pixel Data
                        # 1. Data Elements contained in the Data Set structure shall be encoded with Explicit VR
                        # 2. Encoding of the overall Data Set structure (Data Element Tags, Value Length, ect.) shall be
                        #    in little endian
                        self.explicitVR, self.littleEndian = (True, True)
                elif element.ElementNumber == 0x0000:
                    metalength = element.value
            elif element.GroupNumber == 0x0008:
                if element.ElementNumber == 0x0005:
                    charsets = DCMcharset(element.value)

            if metagroup and self.storage.offset >= 132 + metalength:
                explicitVR = self.explicitVR
                littleEndian = self.littleEndian
                metagroup = False

            if element.GroupNumber == 0x7fe0 and element.ElementNumber == 0x0010:
                # image = bmp.bmp8bit(element.storage.binary[element.storage.offset - element.length:element.storage.offset], 512, 512, 8)
                image = bmp.bmp8bit(512, 512, 8, element.value)
                image.save('/Users/xiongzhen/PycharmProjects/DICOM/dicom.bmp')


class DCMelement:
    def __init__(self, storage, explicitVR = False, littleEndian = True, charset = 'latin_1'):
        self.storage = storage
        self.GroupNumber, self.ElementNumber = struct.unpack('<2H' if littleEndian else '>2H', self.storage[0:4].val())
        self.forward(4)

        if self.GroupNumber == 0x0002:
            explicitVR = littleEndian = True

        if explicitVR:
            if self.GroupNumber == 0xFFFE:
                # Sequence Item

                try:
                    self.VR = DCMattribute[self.GroupNumber][self.ElementNumber][2]
                except KeyError:
                    self.VR = None

                try:
                    self.name = DCMattribute[self.GroupNumber][self.ElementNumber][0]
                except KeyError:
                    if self.ElementNumber == 0x0000:
                        self.name = 'Group Length'
                    else:
                        self.name = ''

                self.length = struct.unpack('<I' if littleEndian else '>I', self.storage[0:4].val())[0]
                self.forward(4)

                self.value = None

            else:
                self.VR = storage[0:2].val().decode('ascii')
                self.forward(2)
                try:
                    self.name = DCMattribute[self.GroupNumber][self.ElementNumber][0]
                except KeyError:
                    if self.ElementNumber == 0x0000:
                        self.name = 'Group Length'
                    else:
                        self.name = ''

                if self.VR in ['OB', 'OW', 'OF', 'SQ', 'UR', 'UT', 'UN']:
                    self.forward(2)     # 0000H reserved
                    self.length = struct.unpack('<I' if littleEndian else '>I', self.storage[0:4].val())[0]
                    self.forward(4)

                    if self.VR == 'SQ':
                        self.value = None
                        return
                    elif self.length == 0xFFFFFFFF:
                        endoffset = self.storage.val().find(b'\xFE\xFF\xDD\xE0' if littleEndian
                                                            else b'\xFF\xFE\xE0\xDD')
                        if endoffset != -1:
                            self.length = endoffset
                else:
                    self.length = struct.unpack('<H' if littleEndian else '>H', self.storage[0:2].val())[0]
                    self.forward(2)

                self.value = DCMvalue(self.storage[0:self.length], self.VR, littleEndian, charset)
                self.forward(self.length)
        else:

            if self.GroupNumber == 0xFFFE:
                # Sequence Item

                try:
                    self.VR = DCMattribute[self.GroupNumber][self.ElementNumber][2]
                except KeyError:
                    self.VR = None

                try:
                    self.name = DCMattribute[self.GroupNumber][self.ElementNumber][0]
                except KeyError:
                    if self.ElementNumber == 0x0000:
                        self.name = 'Group Length'
                    else:
                        self.name = ''

                self.length = struct.unpack('<I' if littleEndian else '>I', self.storage[0:4].val())[0]
                self.forward(4)

                self.value = None

            else:
                try:
                    self.VR = DCMattribute[self.GroupNumber][self.ElementNumber][2]
                except KeyError:
                    if self.ElementNumber == 0x0000:
                        self.VR = 'UL'
                    else:
                        self.VR = 'UN'

                try:
                    self.name = DCMattribute[self.GroupNumber][self.ElementNumber][0]
                except KeyError:
                    if self.ElementNumber == 0x0000:
                        self.name = 'Group Length'
                    else:
                        self.name = ''

                self.length = struct.unpack('<I' if littleEndian else '>I', storage[0:4].val())[0]
                self.forward(4)
                self.value = DCMvalue(self.storage[0:self.length], self.VR, littleEndian, charset)
                self.forward(self.length)

    @property
    def tag(self):
        return self.GroupNumber, self.ElementNumber

    def forward(self, n):
        self.storage.offset += n
        self.storage.length -= n

    def __str__(self):
        if self.length < 1024:
            return '[{0:04x},{1:04x}]({2}){3}: {4}'.format(self.GroupNumber, self.ElementNumber, self.VR, self.name, self.value)
        elif self.length == 0xFFFFFFFF:
            return '[{0:04x},{1:04x}]({2}){3}: {4}'.format(self.GroupNumber, self.ElementNumber, self.VR, self.name,
                                                           '{undefined length}')
        else:
            return '[{0:04x},{1:04x}]({2}){3}:[{4} bytes] {5}'.format(self.GroupNumber,
                                                                self.ElementNumber,
                                                                self.VR,
                                                                self.name,
                                                                int(self.length),
                                                                '{value too long to show}')


class DCMfile:
    def __init__(self, filename):
        self.filename = filename
        self.binary = None
        with open(self.filename, 'rb') as f:
            self.binary = f.read()
        self.storage = DCMstorage(self.binary, 0, -1)
        self.validate()
        self.storage.offset = 132
        self.dataset = DCMdataset(self.storage)

    def validate(self):
        flag = self.storage[128:132].val().decode('ascii')
        if flag != 'DICM':
            raise ValueError('invalid flag')


if __name__ == '__main__':
    def GetFileName():
        import tkinter
        import tkinter.filedialog
        root = tkinter.Tk()

        fg = tkinter.filedialog.LoadFileDialog(root)
        fname = fg.go()
        root.quit()

        return fname

    filename = GetFileName()
    print(filename)
    # filename = r'/Users/xiongzhen/PycharmProjects/DICOM/Detailed/MONO2-[16,12,11]-LittleExplicit-256x256x1-SpP1-PR0'
    # filename = r'/Users/xiongzhen/PycharmProjects/DICOM/Detailed/MONO2-[8,8,7]-LittleImplicit-512x512x1-SpP1-PR0'
    # filename = r'/Users/xiongzhen/PycharmProjects/DICOM/Detailed/MONO2-[8,8,7]-LittleExplicit-120x128x8-SpP1-PR0'
    # filename = r'/Users/xiongzhen/Downloads/DICOM images/71229795'
    # filename = r'/Users/xiongzhen/PycharmProjects/DICOM/Detailed/charset/SCSARAB'
    dcm = DCMfile(filename)