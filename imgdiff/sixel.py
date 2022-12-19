from PIL import Image
from io import BytesIO
import re, os


if os.name == 'nt':
	import msvcrt, sys

	def query(q, end):
		sys.stdout.write(q)
		sys.stdout.flush()

		s = ''
		while True:
			c = msvcrt.getch().decode('ascii')
			s += c
			if c == end:
				break
		return s

elif os.name == 'posix':
	import termios, sys

	def query(q, end):
		fd = sys.stdout.fileno()

		old = termios.tcgetattr(fd)
		tc = termios.tcgetattr(fd)
		tc[3] &= ~(termios.ICANON | termios.ECHO)

		try:
			termios.tcsetattr(fd, termios.TCSANOW, tc)

			sys.stdout.write(q)
			sys.stdout.flush()

			s = ''
			while True:
				c = sys.stdin.read(1)
				s += c
				if c == end:
					break

		finally:
			termios.tcsetattr(fd, termios.TCSANOW, old)

		return s


libsixel = None

def supported_terminal():
	r = query('\033[c', 'c')
	n = re.search(r'\?(.*?)c', r).group(1).split(';')
	return '4' in n


def init():
	try:
		assert supported_terminal()
		import libsixel as _lib
		global libsixel
		libsixel = _lib
		return True
	except:
		return False


def fit(image, size):
	w, h = image.size
	r = min(size[0]/w, size[1]/h)
	w, h = int(r*w), int(r*h)
	return image.resize((w, h))


def limit(image, size):
	w, h = image.size
	r = min(size[0]/w, size[1]/h)
	return image.resize((int(r*w), int(r*h))) if r<1 else image


def to_sixel(image):
	s = BytesIO()
	try:
		data = image.tobytes()
	except NotImplementedError:
		data = image.tostring()
	output = libsixel.sixel_output_new(lambda data, s: s.write(data), s)

	try:
		width, height = image.size
		if image.mode == 'RGBA':
			dither = libsixel.sixel_dither_new(256)
			libsixel.sixel_dither_initialize(dither, data, width, height, libsixel.SIXEL_PIXELFORMAT_RGBA8888)
		elif image.mode == 'RGB':
			dither = libsixel.sixel_dither_new(256)
			libsixel.sixel_dither_initialize(dither, data, width, height, libsixel.SIXEL_PIXELFORMAT_RGB888)
		elif image.mode == 'P':
			palette = image.getpalette()
			dither = libsixel.sixel_dither_new(256)
			libsixel.sixel_dither_set_palette(dither, palette)
			libsixel.sixel_dither_set_pixelformat(dither, libsixel.SIXEL_PIXELFORMAT_PAL8)
		elif image.mode == 'L':
			dither = sixel_dither_get(libsixel.SIXEL_BUILTIN_G8)
			libsixel.sixel_dither_set_pixelformat(dither, libsixel.SIXEL_PIXELFORMAT_G8)
		elif image.mode == '1':
			dither = sixel_dither_get(libsixel.SIXEL_BUILTIN_G1)
			libsixel.sixel_dither_set_pixelformat(dither, libsixel.SIXEL_PIXELFORMAT_G1)
		else:
			raise RuntimeError('unexpected image mode')

		try:
			libsixel.sixel_encode(data, width, height, 1, dither, output)
			return s.getvalue().decode('ascii')
		finally:
			libsixel.sixel_dither_unref(dither)
	finally:
		libsixel.sixel_output_unref(output)
