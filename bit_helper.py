import os
import sys

# param = sys.argv[0]

bitnum = 0

f = open('E:/crow-team.jpg', 'rb')
f.seek(10) # one way
binary = f.read();

rest = binary[10:20] # do a subset

bitstr = ''

def bitlist_to_chars(bl):
	bi = iter(bl)
	bytes = zip(*(bi,) * 8)
	shifts = (7, 6, 5, 4, 3, 2, 1, 0)
	for byte in bytes:
		yield sum(bit << s for bit, s in zip(byte, shifts))

def extract_stream(binary, bitnum):
	bitstr = []
	for byte in binary:
		check = bin(byte)
		bitValue = byte & (1 << bitnum)
		bitstr.append(bitValue)
	return bitstr

bitstr = extract_stream(binary, bitnum)
chars = bitlist_to_chars(bitstr)

with open('e:/binstream.bin', 'wb') as outfile:
		outfile.write(bytearray(i for i in chars))
