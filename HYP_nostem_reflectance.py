import numpy as np
import cv2
import os
import sys

####################### Hyperspectral Image Analysis ##########################################################
###Should follow the data structure of image data: Genotype --> Replicates (Plants) --> HYP folder --> Days --> Images captured by each wavelength###
# the folder name containing image data sets in our defined data structure
mfold = sys.argv[1]
# create a funtion to generate the outline of plant without stem area but keep the leaf area
def rmstem(p705,p750,pic1,pic2,upper_bound,bottom_bound,left_bound,right_bound):
	mypic = []
	control = []
	myl = np.shape(pic1)[0]
	myw = np.shape(pic1)[1]
	y1 = int(upper_bound)
	y2 = int(bottom_bound)
	x1 = int(left_bound)
	x2 = int(right_bound)
	for i in range(myl):
		if i < y1 or i > y2:continue
		for j in range(myw):
			if j < x1 or j > x2:continue
			if pic1[i,j] == 0 or pic2[i,j] == 0:continue
			ndvi = (p750[i,j]-p705[i,j])/(p750[i,j]+p705[i,j])
			ratio = pic1[i,j]/pic2[i,j]
			if ratio <= 1.2: 
				if ndvi > 0.25:
					n = []
					n.append(i)
					n.append(j)
					mypic.append(n)
				else:
					m = []
					m.append(i)
					m.append(j)
					control.append(m)
						
	return mypic,control
# calculate the median intensity of pixels in the non-plant area
def NP(target, pic2):
	final = []
	for k in target:
		i = k[0]
		j = k[1]
		final.append(pic2[i,j])
	fnum = np.median(final)
	return fnum
# calculate the reflectance of each pixel through dividing the median intensity in non-plant area
def reflectance(target, k, pic2):
	final = []
	for a in target:
		i = a[0]
		j = a[1]
		final.append(pic2[i,j]/k)
	return final

# sh is the reference file showing which file corresponds to which wavelength
sh = open('wavelength_foldid.txt','r')
sh.readline()
kdict = {}
# build a library to include file~wavelength information
for line in sh:
	new = line.strip().split('\t')
	kdict[new[-1]] = new[0]
sh.close()

# because of no germination in most of first three days, we just skip them to speed up running the code
first3 = set([])
for i in range(1,4):
	first3.add('Day_'+str(i).zfill(3))

whole = os.listdir(mfold)
				
out = open('HYP_nostem_reflectance_maize_diversity.txt','w')
error = open('HYP_nostem_reflectance_maize_diversity_errorimage.txt','w')
for j1 in whole:
	if j1 == 'Genotype_ZL022':continue
	for i1 in os.listdir('{0}/{1}'.format(mfold,j1)):
			for d1 in sorted(os.listdir('{0}/{1}/{2}/HYP SV 90/'.format(mfold,j1,i1))):
				mdict = {}
				nlist = [i1.replace('Plant_',''),d1]
				if d1 in first3:continue
				# in every folder, the images of 35_0_0.png and 45_0_0.png should be used firstly to calculate NDVI in order to subtract the plant area
				# in every floder, the images of 108_0_0.png and 128_0_0.png were used to subtract the plant stem area
				try:
					m705 = cv2.imread('{0}/{1}/{2}/HYP SV 90/{3}/35_0_0.png'.format(mfold,j1,i1,d1))
					m750 = cv2.imread('{0}/{1}/{2}/HYP SV 90/{3}/45_0_0.png'.format(mfold,j1,i1,d1))
					m1056 = cv2.imread('{0}/{1}/{2}/HYP SV 90/{3}/108_0_0.png'.format(mfold,j1,i1,d1))
					m1151 = cv2.imread('{0}/{1}/{2}/HYP SV 90/{3}/128_0_0.png'.format(mfold,j1,i1,d1))
					# converting plant images from RGB channel to GRAY channel
					tm705 = cv2.cvtColor(m705,cv2.COLOR_BGR2GRAY)
					tm750 = cv2.cvtColor(m750,cv2.COLOR_BGR2GRAY)
					tm1056 = cv2.cvtColor(m1056,cv2.COLOR_BGR2GRAY)
					tm1151 = cv2.cvtColor(m1151,cv2.COLOR_BGR2GRAY)
					tm1056 = tm1056.astype(np.float)
					tm1151 = tm1151.astype(np.float)
					tm705 = tm705.astype(np.float)
					tm750 = tm750.astype(np.float)
					# defining the interested area by removing the metal frame and pot carrier.
					rmg,back = rmstem(tm705,tm750,tm1056,tm1151,45,467,30,273)
					for i in os.listdir('{0}/{1}/{2}/HYP SV 90/{3}'.format(mfold,j1,i1,d1)):
						# since first two images are just information of hyperspectral images and not useful for further analysis
						if i == '0_0_0.png':continue
						if i == '1_0_0.png':continue
						name = i.replace('_0_0.png','')
						try:
							t = cv2.imread('{0}/{1}/{2}/HYP SV 90/{3}/{4}'.format(mfold,j1,i1,d1,i))
							t = t.astype(np.float)
							t1 = t[:,:,0]
							cint = NP(back,t1)
							total = reflectance(rmg,cint,t1)
							avg = np.median(total)
							mdict[name] = avg
						except:
							error.write(i1+'\t'+d1+'\t'+i+'\n')
					for i in range(2,245):
						i = str(i)
						if i not in mdict:
							nlist.append('NA')
						else:
							nlist.append(str(mdict[i]))
				except:
					error.write(i1+'\t'+d1+'\n')
				out.write('\t'.join(nlist)+'\n')
out.close()
error.close()
