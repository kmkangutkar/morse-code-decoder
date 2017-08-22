from scipy.io.wavfile import read as wav_read
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment    #pip install pydub, apt-get install ffmpeg
import sys
import os

MORSECODE = "##TEMNAIOGKDWRUS##QZYCXBJP#L#FVH09#8###7######=61####+##2###3#45"
IGNORE_ZERO_LIMIT = 11
SAMPLER_CONST = 3295
NEXT_LETTER_LIMIT = 51

def plot_audio(sampled_audio):
	plt.plot(sampled_audio[0:len(sampled_audio)])
	plt.ylabel("Amplitude");
	plt.xlabel("Time (samples)");
	plt.title("MORSE SAMPLE")
	plt.show()

def get_mid_range(sampled_audio, low, high):
	index_audio = []
	for i in range(len(sampled_audio)):
		p = sampled_audio[i]
		if p >= low and p <= high:
			index_audio.append(1)
		elif p < low:
			index_audio.append(0)
	return index_audio

def convert_to_zero_one_sum(index_audio):
#	y = list(x[0] for x in [d.values() for d in index_audio])
	y = index_audio
	counter = 0
	count_zero = 0
	prev = 0
	print_counter = 0
	i = 0
#	print "Length", len(y)
	zero_one = []
	while i < len(y):
		if prev == y[i]:
			counter += 1
		else:
			if(prev == 1) and (y[i] == 0):
				while(i < len(y) and y[i] == 0):
					count_zero += 1
					i += 1
			     
				if count_zero <= IGNORE_ZERO_LIMIT:
					i -= 1
					counter += count_zero   
				else:
	 #                       	print prev, ":", counter
					zero_one.append((prev, counter))
					counter = count_zero
					prev = 0
				if i >= len(y):
#                        	print prev, ":", counter
					zero_one.append((prev, counter))
			
				count_zero = 0
			else:
#                        print prev, ":", counter,
				zero_one.append((prev, counter))
				prev = y[i]
				counter = 1
		i += 1
	return zero_one

def decode(zero_one):
	#select 1 counts
	x = list(y[1] for y in zero_one if y[0]==1)
	#find average 1 counts
	divider =  sum(x)/len(x)
#	print divider
	result = ""
	morse_index = "1"
	for x in zero_one:
		if x[0] == 1:	
			if x[1] <= divider:
				#dit
				morse_index += '1' 
#			print '.',
			else:
				#dah
				morse_index += '0'
#			print '-',
		else:
			if x[1] >= NEXT_LETTER_LIMIT: 
				index = int(morse_index, 2)
				if index < len(MORSECODE):
					result += MORSECODE[index]	
				else:
					result += '^'
				morse_index = '1'
	return result

def sample(audio, sampler, flag):
	sampled_audio = []
	sample_counter = 0
	for x in audio:
		if flag == 1:
			x = x[0]
		if (sample_counter % sampler == 0):
			if x < 0:
				x = -x
			sampled_audio.append(x)
		sample_counter += 1
	return sampled_audio

def convert_to_wav(mp3file, filename):
	sound = AudioSegment.from_mp3(mp3file)
	wavfile = filename + ".wav"
	sound.export(wavfile, format="wav")
	return wavfile
		
def main():
#take audio (.wav .mp3) file as cl argument
	if len(sys.argv) > 1:
		try:
			filename, file_extension = os.path.splitext(sys.argv[1])
			#if format mp3 convert to wav
			if file_extension == ".mp3":
				openfile = convert_to_wav(sys.argv[1], filename)
			else:
				openfile = sys.argv[1] 
			input_data = wav_read(openfile)
		except IOError:
			print "Please input valid .wav or .mp3 file"
			exit(0)

	else:
		print "Please input audio (.wav / .mp3) file"
		exit(0)
#set flag if the audio is double channel
	if type(input_data[1][0]) == np.ndarray:
		#double channel
		flag = 1
	else:
		#single channel
		flag = 0
	audio = input_data[1];
#set sampler value
	sampler = len(audio) / SAMPLER_CONST
	print sampler, len(audio)
#sample audio at sampler rate
	sampled_audio = sample(audio, sampler, flag)
#find mid range 
	max_amp = max(sampled_audio)
	min_amp = min(sampled_audio)
	mid = max_amp / 2
	high = mid + mid / 2
	low = mid - mid / 2
#plot sampled_audio	
	plot_audio(sampled_audio)
#if audio value in mid range then = 1 else = 0
	index_audio = get_mid_range(sampled_audio, low, high)
#sum consecutive ones and zeros
	zero_one = convert_to_zero_one_sum(index_audio)
#decode zero == off and one == on
	result = decode(zero_one)
	print result

if __name__ == "__main__":
	main()
