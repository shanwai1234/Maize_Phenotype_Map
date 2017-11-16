import numpy as np
import cv2 
import sys
import os
#######################RGB Image Data Analysis############################################################
###Should follow the data structure of image data: Genotype --> Replicates (Plants) --> Different Views --> Image captured by each Day###
# mfold defines the folder name that stores the data in our data structure
mfold = sys.argv[1]
# The ratio between pixels further zoom level and closer zoom level is 1:2.02, each pixel in closer zoom level is 0.746mm. This script generates values based on pixel counts.
# binary function is going to extract green pixels by defined threshold of (2*G)/(R+B) > 1.15
def binary(pic,upper,bottom,left,right):
	mypic = []
	myl = np.shape(pic)[0]
	myw = np.shape(pic)[1]
	x1 = left
	x2 = right
	y1 = upper
	y2 = bottom
	for iind,i in enumerate(pic):
		if iind < y1 or iind > y2:
			n = [0]*myw
		else:
			n = []
			for jind,j in enumerate(i):
				if j > 1.15:
					if jind < x1 or jind > x2:
						t = 0
					else:
						t = 255
				else:
					t = 0 
				n.append(t)
		mypic.append(n)
	mypic = np.array(mypic)
	return mypic
# create a function to extract values of plant height, plant width and plant area pixel counts
def call_numeric(thresh):
	hh = 0
	ww = 0
	aa = 0
	areas = []
	contours,hierarchy = cv2.findContours(thresh, 1, 2)
	for c in contours:
		areas.append(cv2.contourArea(c))
	people = np.array(contours)
	ages = np.array(areas)
	inds = ages.argsort()
	sortedcontours = people[inds]
	cnt = sortedcontours[-1]
	hull = cv2.convexHull(cnt)
	x,y,w,h = cv2.boundingRect(cnt)
	hh = str(h)
	ww = str(w)
	aa = str(cv2.contourArea(hull))
	return hh,ww,aa,areas

whole = os.listdir(mfold)

# because two zoom levels were applied on the RGB images in different days, and we analyze plant images in two zoom levels
close = set([])
far = set([])
for i in range(1,27):
	close.add('Day_'+str(i).zfill(3))
close.remove('Day_'+str(11).zfill(3))
for i in range(27,33):
	far.add('Day_'+str(i).zfill(3))
far.add('Day_'+str(11).zfill(3))

# out is the file with extracted numeric values from RGB images
out = open('RGB_extraction.csv','w')

# create this file to trace some image files that can not load correctly to make sure the whole loop can go correctly
error = open('RGB_extraction_error.csv','w')

out.write('PlantID'+'\t'+'Date'+'\t'+'View'+'\t'+'Plant Height'+'\t'+'Plant Width'+'\t'+'Projected Plant Area'+'\n')
views = ['VIS SV 0','VIS SV 90']
for j1 in sorted(whole):
	if j1 == 'Genotype_ZL022':continue
	for i1 in os.listdir('{0}/{1}'.format(mfold,j1)):
		for v in views:
			for d1 in sorted(os.listdir('{0}/{1}/{2}/{3}/'.format(mfold,j1,i1,v))):
				nlist = [i1,d1.replace('.png','')]
				myview = 'View'+v.replace('VIS SV ','')
				na = [myview,'NA','NA','NA'] 
				date = d1.replace('.png','')
				try:
					abc = cv2.imread('{0}/{1}/{2}/{3}/{4}'.format(mfold,j1,i1,v,d1))
					abc = abc.astype(np.float)
					imgreen = (2*abc[:,:,1])/(abc[:,:,0]+abc[:,:,2])
					if date in close:
						thresh = binary(imgreen,50,1950,335,2280)
					elif date in far:
						thresh = binary(imgreen,50,1450,815,1780)
					cv2.imwrite('test.jpg',thresh)
					thresh = cv2.imread("test.jpg",cv2.CV_LOAD_IMAGE_GRAYSCALE)
					h,w,area,areas0 = call_numeric(thresh)
					total = max(areas0)
					k = areas0.index(total)
					del areas0[k]
					for i in areas0:
						total -= i
					nlist.append(myview)
					if date in far:
						nlist.append(str(float(h)*2.02))
						nlist.append(str(float(w)*2.02))
						nlist.append(str(float(total)))
					else:
						nlist.append(h)
						nlist.append(w)
						nlist.append(total)
				except:
					nlist.extend(na)
					error.write(j1+':'+i1+':'+v+':'+d1+'\n')
				out.write('\t'.join(nlist)+'\n')
out.close()
error.close()
