import numpy as np
import cv2 
from matplotlib import pyplot as plt
import sys
import os
import fnmatch

#######################RGB Image Data Analysis############################################################
###Should follow the data structure of image data: Genotype --> Replicates (Plants) --> Different Views --> Image captured by each Day###
mfold = sys.argv[1]
whole = os.listdir(mfold)
# binary function is going to count intensity of red pixels greater than 70 and get the sum and average fluorescence intensity in detected plant area
def binary(pic,upper,bottom,left,right):
	mypic = []
	total = 0
	k = 0
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
				if j > 70:
					if jind < x1 or jind > x2:
						t = 0
					else:
						k += 1
						total += j
						t = 255
				else:
					t = 0 
				n.append(t)
		mypic.append(n)
	mypic = np.array(mypic)
	avg = total/k
	return mypic,total,avg

# because two zoom levels were applied on the Fluo images in different days, and we analyze plant images in two zoom levels
close = set([])
far = set([])
for i in range(1,27):
        close.add('Day_'+str(i).zfill(3))
close.remove('Day_'+str(11).zfill(3))
for i in range(27,33):
        far.add('Day_'+str(i).zfill(3))
far.add('Day_'+str(11).zfill(3))

# out is the file with extracted numeric values from Fluo images
out = open('Fluo_extraction.csv','w')
out.write('PlantID'+'\t'+'Date'+'\t'+'View'+'\t'+'Sum of intensity'+'\t'+'Average of intensity'+'\n')

# out is the file with extracted numeric values from Fluo images
error = open('Fluo_extraction_error.csv','w')

views = ['Fluo SV 0','Fluo SV 90','Fluo TV 0']
for j1 in sorted(whole):
	if j1 == 'Genotype_ZL022':continue
	for i1 in os.listdir('{0}/{1}'.format(mfold,j1)):
		for v in views:
			for d1 in sorted(os.listdir('{0}/{1}/{2}/{3}/'.format(mfold,j1,i1,v))):
				nlist = [i1,d1.replace('.png','')]
				myview = 'View'+' '+v.replace('Fluo ','')
				na = [myview,'NA','NA'] 
				date = d1.replace('.png','')
				try:
					abc = cv2.imread('{0}/{1}/{2}/{3}/{4}'.format(mfold,j1,i1,v,d1))
					abc = abc.astype(np.float)
					imgreen = abc[:,:,2]
					if myview == 'TV 0':
						thresh0,total,avg = binary(imgreen90,5,1038,5,1390)
					else:
						if date in close:
							thresh0,total,avg = binary(imgreen,210,1000,130,900)
						elif date in far:
							thresh0,total,avg = binary(imgreen,198,912,232,800)
					cv2.imwrite('fluo.jpg',thresh0)
					nlist.append(myview)
					nlist.append(str(total))
					nlist.append(str(avg))
				except:
					nlist.extend(na)
					error.write(j1+':'+i1+':'+v+':'+d1+'\n')
				out.write('\t'.join(nlist)+'\n')
out.close()
error.close()
