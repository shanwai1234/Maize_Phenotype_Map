import numpy as np
import cv2 
from matplotlib import pyplot as plt
import os
import sys
from scipy import linalg as LA
from matplotlib import cm

##############################Hyperspectral Image PCA Visualization#####################################################################################################################
##############################Notice: Since all pixels were analyzed at once, more Images to be analyzed, expotential time will be cost !!!#############################################
# Copy any PlantID folder you are interested to 'test_HYP'
mfold = sys.argv[1]

# Create function PCA2 to generate first three PC coefficents for all analyzed image data
def PCA2(data, dims_rescaled_data=3):
	"""
	returns: data transformed in 2 dims/columns + regenerated original data
	pass in: data as 2D NumPy array
	"""
	m, n = data.shape
	# mean center the data
	data -= data.mean(axis=0)
	# calculate the covariance matrix
	R = np.cov(data, rowvar=False)
	# calculate eigenvectors & eigenvalues of the covariance matrix
	# use 'eigh' rather than 'eig' since R is symmetric, 
	# the performance gain is substantial
	evals, evecs = LA.eigh(R)
	# sort eigenvalue in decreasing order
	idx = np.argsort(evals)[::-1]
	evecs = evecs[:,idx]
	# sort eigenvectors according to same index
	evals = evals[idx]
	# select the first n eigenvectors (n is desired dimension
	# of rescaled data array, or dims_rescaled_data)
	evecs = evecs[:, :dims_rescaled_data]
	# carry out the transformation on the data using eigenvectors
	# and return the re-scaled data, eigenvalues, and eigenvectors
	return np.dot(evecs.T, data.T).T, evals, evecs
# Seperating all analyzed pixels using the first two PCs
def plot_pca(data):
	clr1 =  '#2026B2'
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	data_resc, data_orig,a = PCA2(data)
	ax1.plot(data_resc[:, 0], data_resc[:, 1], '.', mfc=clr1, mec=clr1)
	plt.show()
	return data_resc
# Using NDVI to segment all plant area by defining threshold greater than 0.25
def rmstem(p705,p750,upper_bound,bottom_bound,left_bound,right_bound):
	mypic = []
	control = []
	myl = np.shape(p705)[0]
	myw = np.shape(p705)[1]
	y1 = int(upper_bound)
	y2 = int(bottom_bound)
	x1 = int(left_bound)
	x2 = int(right_bound)
	for i in range(myl):
		if i < y1 or i > y2:continue
		for j in range(myw):
			if j < x1 or j > x2:continue
			ndvi = (p750[i,j]-p705[i,j])/(p750[i,j]+p705[i,j]) 
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
# Calculating the median intensity of pixels in the non-plant area
def NP(target, pic2):
	final = []
	for k in target:
		i = k[0]
		j = k[1]
		final.append(pic2[i,j])
	fnum = np.median(final)
	return fnum
# Storing the reflectance of each pixel and their corresponding positions in the original image
def PCA(target, k, pic2, n):
	final = {}
	for a in target:
		i = a[0]
		j = a[1]
		myname = "{0}-{1}-{2}".format(i,j,n)
		final[myname] = pic2[i,j]/k
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

ll = []
whole = os.listdir(mfold)
mdict = {}
tlist = []
# The date you want to visualize, e.g. Day_028
date = sys.argv[2]
for j1 in whole:
	tlist.append(j1)
	for i1 in os.listdir('{0}/{1}/HYP SV 90/'.format(mfold,j1)):
		if i1 != date:continue  
		subset = os.listdir('{0}/{1}/HYP SV 90/{2}'.format(mfold,j1,i1))
		# in every folder, the images of 35_0_0.png and 45_0_0.png should be used firstly in order to subtract the plant area
		if True:
			m705 = cv2.imread('{0}/{1}/HYP SV 90/{2}/35_0_0.png'.format(mfold,j1,i1))
			m750 = cv2.imread('{0}/{1}/HYP SV 90/{2}/45_0_0.png'.format(mfold,j1,i1))
			# converting plant images from RGB to GRAY channel
			tm705 = cv2.cvtColor(m705,cv2.COLOR_BGR2GRAY)
			tm750 = cv2.cvtColor(m750,cv2.COLOR_BGR2GRAY)		
			tm705 = tm705.astype(np.float)
			tm750 = tm750.astype(np.float)
			# defining the interested area that we are going to analyze the plant
			rmg,back = rmstem(tm705,tm750,45,445,30,273)
			for i in subset:
				# first two images are not useful and just skip them
				if i == '0_0_0.png':continue
				if i == '1_0_0.png':continue
				# info.txt is not an image file
				if i == 'info.txt':continue
				name = i.replace('_0_0.png','')
				t = cv2.imread('{0}/{1}/HYP SV 90/{2}/{3}'.format(mfold,j1,i1,i))
				t = t.astype(np.float)
				t1 = t[:,:,0]
				# multiply each files in the folder with the binarized image. For each pixel, dividing 255 to make each pixel in 0~1 
				cint = NP(back,t1)
				total = PCA(rmg,cint,t1,j1)
				if name not in mdict:
					mdict[name] = {}
				mdict[name].update(total)
			wavelengths = list(mdict)
                	pixels = list(mdict[wavelengths[0]])
		else:
			print j1
for p in pixels:
	ll.append([])
	for w in wavelengths:				
		ll[-1].append(mdict[w][p])
ll_array = np.array(ll)
data_resc = plot_pca(ll_array)

myxvals = {}
myyvals = {}
mycvals = {}
myplant = set([])
for x in range(3):
	mytitle = "PC {0}".format(x+1)
	for name,val in zip(pixels,data_resc[:,x]):
		l = map(int,name.split('-')[:2])
		myplant.add(name.split('-')[2])
		myid = 'PC'+str(x)+'-'+name.split('-')[2]
		if myid not in myxvals:
			myxvals[myid] = []
			myyvals[myid] = []
			mycvals[myid] = []
		myyvals[myid].append(l[0]*(-1))
		myxvals[myid].append(l[1])
		mycvals[myid].append(val)
	
n = 0
myxtick = []
myxname = []
ncvals = {}
for i in myplant:
	myxname.append(i)
	pc0 = 'PC0'+'-'+i
	pc1 = 'PC1'+'-'+i
	pc2 = 'PC2'+'-'+i
	if i not in ncvals:
		ncvals[i] = {}
	ncvals[i][pc0] = []
	ncvals[i][pc1] = []
	ncvals[i][pc2] = []
	# b is real value of pc value, a is the position of pc value
	for a,b in enumerate(mycvals[pc0]):
		name = str(myyvals[pc0][a])+'-'+str(myxvals[pc0][a])
		if name not in ncvals[i]:
			ncvals[i][name] = []
		# normalize PCA components for each plant of each genotype by the formula: normalized_value = (value-min_value)/(max_value-min_value) 
		ncvals[i][name].append((mycvals[pc0][a]-min(mycvals[pc0]))/(max(mycvals[pc0])-min(mycvals[pc0])))
		ncvals[i][name].append((mycvals[pc1][a]-min(mycvals[pc1]))/(max(mycvals[pc1])-min(mycvals[pc1])))
		ncvals[i][name].append((mycvals[pc2][a]-min(mycvals[pc2]))/(max(mycvals[pc2])-min(mycvals[pc2])))

n = 0
plt.show()
fig = plt.figure()
ax = fig.add_subplot('111')
num = 0
for i in myplant:
	xvals = []
	yvals = []
	cvals = []
	pc0 = 'PC0'+'-'+i
	nx = max(myxvals[pc0])-min(myxvals[pc0])
	ny = max(myyvals[pc0])-min(myyvals[pc0])
	for ii in range(nx):
		x = ii + min(myxvals[pc0])
		for jj in range(ny):
			y = jj + min(myyvals[pc0])
			pos = str(y)+'-'+str(x)
			if pos in ncvals[i]:
				clist = ncvals[i][pos]
				xvals.append(ii+num*250)
				yvals.append(jj)
				cvals.append((clist[0],clist[1],clist[2]))
	myxtick.append(np.median(xvals))
	myxname.append(i)
	num += 1
	ax.scatter(xvals,yvals,color=cvals)
ax.set_xticks(myxtick)
ax.set_xticklabels(myxname)
ax.set_yticklabels([])
plt.show()
