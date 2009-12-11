

from bz2 import compress
from base64 import encodestring


logo = 'cuecutter-plain.svg'

svg = file(logo).read()

if not svg.startswith('<?xml') \
        or '<svg' not in svg \
        or ':sodipodi' in svg \
        or ':inkscape' in svg:
    print '%s is not a plain svg file' % logo

b64_logo = encodestring(compress(svg))


file('cuecutter', 'w').write(file('cuecutter.py').read().replace('@BITMAP@', b64_logo))


