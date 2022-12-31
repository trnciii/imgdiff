import argparse, numpy as np
from PIL import Image, ImageChops
from .ayame import sixel

def main():
	parser = argparse.ArgumentParser()

	parser.add_argument('a')
	parser.add_argument('b')
	parser.add_argument('--abs', action='store_true')
	parser.add_argument('-n', '--negative', action='store_true')
	parser.add_argument('-o')
	parser.add_argument('-b', '--background', action='store_true')
	parser.add_argument('-x', '--multiply', type=int, default=1)

	args = parser.parse_args()

	a = np.asarray(Image.open(args.a).convert('RGB')).astype(np.int16)
	b = np.asarray(Image.open(args.b).convert('RGB')).astype(np.int16)

	if a.shape != b.shape:
		print('cannot compare images of different sizes')
		return


	diff = np.abs(a-b) if args.abs else np.maximum(0, b-a) if args.negative else np.maximum(0, a-b)
	diff *= args.multiply

	ret = Image.fromarray(diff.astype(np.uint8))

	if (not args.background) and sixel.init():
		print(sixel.to_sixel(ret), end='')

	if args.o:
		ret.save(args.o)


if __name__ == '__main__':
	main()