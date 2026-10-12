#!/usr/bin/env python3
"""Transfer only generated charcoal pigment onto vacant ancestral rock."""
import hashlib
import json
from pathlib import Path
import struct
import zlib
from make_thumbnail import png_rgb

SOURCE_HASH = 'dceafc14303f22e203ee0ba20b812094d33ed9c2d0bd7575a1af182b90456f0e'


def png(width, height, rows):
    def chunk(kind, data):
        body = kind + data
        return struct.pack('>I',len(data)) + body + struct.pack('>I',zlib.crc32(body))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))
            + chunk(b'IDAT',zlib.compress(b''.join(b'\0'+bytes(row) for row in rows),9))
            + chunk(b'IEND',b''))


def main():
    source = Path('artifacts/gathering/wall.png')
    target = Path('artifacts/gathering/wall-v4.png')
    original = source.read_bytes()
    if hashlib.sha256(original).hexdigest() != SOURCE_HASH:
        raise ValueError('requires unchanged record-03 wall and generated insert')
    width,height,rows = png_rgb(original)
    iw,ih,insert = png_rgb(target.read_bytes())
    # Crop only the dark motif in memory; white contributes no pigment.
    points = [(x,y) for y,row in enumerate(insert) for x in range(iw)
              if min(row[x*3:x*3+3]) < 120]
    x0,x1 = min(x for x,y in points)-3,max(x for x,y in points)+4
    y0,y1 = min(y for x,y in points)-3,max(y for x,y in points)+4
    left,top,pw,ph = 260,270,165,110
    result = [bytearray(row) for row in rows]
    changed = 0
    for y in range(ph):
        sy = y0 + y*(y1-y0)//ph
        for x in range(pw):
            sx = x0 + x*(x1-x0)//pw
            value = sum(insert[sy][sx*3:sx*3+3])/3
            opacity = max(0,min(1,(230-value)/210)) * .78
            if opacity == 0: continue
            i = (left+x)*3
            old = rows[top+y][i:i+3]
            # Keep underlying stone relief visible through worn pigment.
            new = bytes(round(v*(1-opacity) + c*opacity)
                        for v,c in zip(old,(33,25,18)))
            result[top+y][i:i+3] = new
            changed += new != old
    outside = sum(rows[y][x*3:x*3+3] != result[y][x*3:x*3+3]
                  for y in range(height) for x in range(width)
                  if not (left<=x<left+pw and top<=y<top+ph))
    assert changed>500 and outside==0
    encoded = png(width,height,result)
    target.write_bytes(encoded)
    source.write_bytes(encoded)
    receipt = {'source_sha256': SOURCE_HASH,'wall_sha256':hashlib.sha256(encoded).hexdigest(),
               'rectangle':dict(x=left,y=top,width=pw,height=ph),
               'changed_pixels':changed,'changed_pixels_outside_rectangle':outside,
               'dimensions':[width,height],'format':'8-bit RGB PNG',
               'method':'Generated charcoal only; white removed in memory, stone texture retained.'}
    Path('gathering/checks/round-04/image-preservation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
