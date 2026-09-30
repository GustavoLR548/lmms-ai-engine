"""Minimal SoundFont 2 reader: lists presets (bank/program/name) and, per preset, the key ranges and
sample names of its zones - enough to find which key plays which drum in a kit.

    python sf2info.py file.sf2              # presets
    python sf2info.py file.sf2 128 40       # key map of bank 128 program 40
"""
import struct
import sys


def _chunks(data, start, end):
    i = start
    while i + 8 <= end:
        cid, size = data[i:i + 4], struct.unpack('<I', data[i + 4:i + 8])[0]
        yield cid, i + 8, size
        i += 8 + size + (size & 1)


def _records(buf, fmt):
    n = struct.calcsize(fmt)
    return [struct.unpack(fmt, buf[i:i + n]) for i in range(0, len(buf) - n + 1, n)]


def _name(b):
    return b.split(b'\0')[0].decode('latin-1').strip()


class SF2:
    def __init__(self, path):
        data = open(path, 'rb').read()
        assert data[:4] == b'RIFF' and data[8:12] == b'sfbk', 'not a SoundFont 2 file'
        pdta = {}
        for cid, off, size in _chunks(data, 12, len(data)):
            if cid == b'LIST' and data[off:off + 4] == b'pdta':
                for sid, soff, ssize in _chunks(data, off + 4, off + size):
                    pdta[sid.decode()] = data[soff:soff + ssize]
        self.phdr = [(_name(r[0]), r[1], r[2], r[3]) for r in _records(pdta['phdr'], '<20sHHHIII')]
        self.pbag = _records(pdta['pbag'], '<HH')
        self.pgen = _records(pdta['pgen'], '<HH')
        self.inst = [(_name(r[0]), r[1]) for r in _records(pdta['inst'], '<20sH')]
        self.ibag = _records(pdta['ibag'], '<HH')
        self.igen = _records(pdta['igen'], '<HH')
        self.shdr = [_name(r[0]) for r in _records(pdta['shdr'], '<20sIIIIIBbHH')]

    def presets(self):
        """[(bank, program, name)] sorted."""
        return sorted((b, p, n) for n, p, b, _ in self.phdr[:-1])

    @staticmethod
    def _zones(bags, gens, first, last):
        for z in range(first, last):
            g0, g1 = bags[z][0], bags[z + 1][0]
            yield {op: amt for op, amt in gens[g0:g1]}

    def keymap(self, bank, program):
        """[(lo, hi, instrument, sample)] for one preset."""
        idx = next(i for i, (n, p, b, _) in enumerate(self.phdr[:-1]) if b == bank and p == program)
        out = []
        for pz in self._zones(self.pbag, self.pgen, self.phdr[idx][3], self.phdr[idx + 1][3]):
            if 41 not in pz:
                continue
            plo, phi = (pz[43] & 0xFF, pz[43] >> 8) if 43 in pz else (0, 127)
            iname, ib0 = self.inst[pz[41]]
            ib1 = self.inst[pz[41] + 1][1]
            for iz in self._zones(self.ibag, self.igen, ib0, ib1):
                if 53 not in iz:
                    continue
                lo, hi = (iz[43] & 0xFF, iz[43] >> 8) if 43 in iz else (0, 127)
                lo, hi = max(lo, plo), min(hi, phi)
                if lo <= hi:
                    out.append((lo, hi, iname, self.shdr[iz[53]]))
        return sorted(set(out))


if __name__ == '__main__':
    sf = SF2(sys.argv[1])
    if len(sys.argv) > 3:
        for lo, hi, inst, smp in sf.keymap(int(sys.argv[2]), int(sys.argv[3])):
            print(f'{lo:3d}-{hi:3d}  {inst:20s} {smp}')
    else:
        for b, p, n in sf.presets():
            print(f'{b:3d} {p:3d}  {n}')
