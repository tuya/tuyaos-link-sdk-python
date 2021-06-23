#!/usr/bin/env python
"""
qr - Convert stdin (or the first argument) to a QR Code.

When stdout is a tty the QR Code is printed to the terminal and when stdout is
a pipe to a file an image is written. The default image format is PNG.
"""
import sys
import optparse
import os
import qrcode
# The next block is added to get the terminal to display properly on MS platforms
if sys.platform.startswith(('win', 'cygwin')):  # pragma: no cover
    import colorama
    colorama.init()

default_factories = {
    'pil': 'qrcode.image.pil.PilImage',
    'pymaging': 'qrcode.image.pure.PymagingImage',
    'svg': 'qrcode.image.svg.SvgImage',
    'svg-fragment': 'qrcode.image.svg.SvgFragmentImage',
    'svg-path': 'qrcode.image.svg.SvgPathImage',
}

error_correction = {
    'L': qrcode.ERROR_CORRECT_L,
    'M': qrcode.ERROR_CORRECT_M,
    'Q': qrcode.ERROR_CORRECT_Q,
    'H': qrcode.ERROR_CORRECT_H,
}

def qrcode_generate(data):
    qr = qrcode.QRCode(error_correction=error_correction['M'])

    image_factory = None

    qr.add_data(data)

    if image_factory is None and os.isatty(sys.stdout.fileno()):
        qr.print_ascii(tty=True)
        return

    img = qr.make_image()

    sys.stdout.flush()
    # Use sys.stdout.buffer if available (Python 3), avoiding
    # UnicodeDecodeErrors.
    stdout_buffer = getattr(sys.stdout, 'buffer', None)
    if not stdout_buffer:
        if sys.platform == 'win32':  # pragma: no cover
            import msvcrt
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        stdout_buffer = sys.stdout

    img.save(stdout_buffer)
