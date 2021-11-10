'''

Script by: Gabriele Bendetti

date: 25/06/2021

Utilities functions. This file is used to have a more organized main script. It contains:

+ Random plane orientation generator that can be used to practice plane attitude interpretation
+ Random fold generator 
+ Plotter
+ Data converter from pandas dataframe to dict following the format used in plane_plot

'''



import numpy as np
import matplotlib.pyplot as plt
import mplstereonet
import obspy.imaging.beachball as bb
import mplstereonet as mpl





def random_plane_gen(sets=1, n_planes=1):

	r_dipdir = np.random.randint(0,361,sets) #random dipdir

	r_dip = np.random.randint(0,91,sets) #random dip

	r_std = np.random.randint(5,20,sets) #random std
	
	planes_dict = {x:{'dd':0,'d':0} for x in range(sets)}

	for nset,dd,d,std in zip(list(range(sets)),r_dipdir,r_dip,r_std):
	
		planes_dict[nset]['s'] = np.abs(np.round(np.random.normal(dd,std,n_planes),2))
		planes_dict[nset]['d'] = np.abs(np.round(np.random.normal(d,std,n_planes),2))
		#print(f'set {nset}:{(dd+90)%360}/{d}')
		#print(planes_dict)
		
	return planes_dict


def random_folds_gen(sets=1,n_planes=1):

	def axial_plane_finder(profile_plane,limb_s,limb_d):
		
		'''
		The axial plane can be defined in the pi plot by calculating the bisector of the interlimb angle. The bisector is the pole of the axial plane. To find the bisector position (as a pole we can 		calculate the angle between the two poles and compare it with the interlimb angle. The angle value can be added to the pole2_index to find the index of the bisector pole. 
		
		caveat: this method needs to have prior knowledge of the approximate interlimb angle.
		'''
		
		angle = int(np.degrees(mpl.angular_distance(mpl.pole(limb_s[0],limb_d[0]),mpl.pole(limb_s[1],limb_d[1]))))
		

		if not np.isclose(angle,i,atol=5):

			angle = int(180-np.degrees(mpl.angular_distance(mpl.pole(limb_s[0],limb_d[0]),mpl.pole(limb_s[1],limb_d[1]))))


		bisector_s,bisector_d = s[int(pole2_index+(angle/2))],d[int(pole2_index+(angle/2))]
		return bisector_s,bisector_d
	 
	'''
	The axial plane inclination and hinge line plunge are correlated by the fleuty diagram. 

	This is a triangle with ax_angle as the base and plunge as the height. By choosing at random an axial plane inclination the plunge of the hinge line can be calculated by 
		h = b*tan(alpha) 
		
	where alpha is the inclination angle of the hypothenuse in respect to the horizontal. 
	If alpha is 0 --> the fold is horizontal
	If alpha is 45 --> the fold is reclined (plunge=ax_inclination)
	'''


	r_ax_angle = np.random.uniform(0,1,sets)*90
	alpha = np.deg2rad(np.random.randint(0,46,sets))
	plunge = r_ax_angle*np.tan(alpha)

	r_fold_profile_dd = np.random.randint(0,361,sets) #dip direction of the profile plane
	r_fold_profile_s = (r_fold_profile_dd-90)%360
	r_fold_profile_d = np.abs(plunge-90) #dip of the profile plane. This implicitly controls the plunge of the hinge line


	'''
	To plot the position of a pole we can use the functions mpl.plane and geographic2pole. The first funcion gives an array of values rappresenting points coordinate (lat, lon) of the profile plane (the angular resolution is given by the [segment] parameter). After obtaining the array the (lat, lon) values are converted to trend and plunge with the function mpl.geographic2pole giving all the possibile poles lying ont he profile plane. 

	With the list of possible poles is just a matter of obtaining the array indicies. 

	The first step (seg) is to determine the index based only on the interlimb angle. This is calculated by interlimb/2 (because the interlimb is the angle between the two poles or planes). Because of this in the index for the second plane seg is negative (symmetrical).
	The second step (seg_rot) is to modify the index based on the inclination of the axial plane. This is calculated by subtracting 90° to the ax_angle value (this is because the ax_inclination in the fleuty diagram is calculated from the vertical).

	These are the values that determine the indicies (pole1_index and pole2_index) for the generator limb poles.

	'''   

	r_i = np.random.randint(0,181,sets) # interlimb angle
	r_std = np.random.randint(5,15,sets)
	
	folds_dict = {x:{'s':0,'d':0,'axial_s':0,'axial_d':0} for x in range(sets)}
	
	for nset,i,ax_angle,fold_profile_s,fold_profile_d,std in zip(list(range(sets)),r_i,r_ax_angle,r_fold_profile_s, r_fold_profile_d, r_std):
	
		seg = int((i/2)) #segment that represent the fold limb given an angle from the center
		seg_rot = int(90-ax_angle) # quantity to add to the segment to rotate the limbs given an axial plane inclination

		pole1_index = seg+seg_rot
		pole2_index = (-seg-1)+seg_rot

		lon,lat = mpl.plane(fold_profile_s,fold_profile_d,segments=181) 

		s,d= mpl.geographic2pole(lon,lat)

		fold_limb_s,fold_limb_d = [*s[pole1_index],*s[pole2_index]],[*d[pole1_index],*d[pole2_index]]
		bisector_s,bisector_d = axial_plane_finder((fold_profile_s,fold_profile_d),fold_limb_s,fold_limb_d) #this is the axial plane
		
		ndist_limb_dd = np.array([np.random.normal(fold_limb_s[0],std,n_planes),np.random.normal(fold_limb_s[1],std,n_planes)])
		ndist_limb_d = np.array([np.random.normal(fold_limb_d[0],std,n_planes),np.random.normal(fold_limb_d[1],std,n_planes)])
		folds_dict[nset]['s'] = np.abs(np.round(ndist_limb_dd,2))
		folds_dict[nset]['d'] = np.abs(np.round(ndist_limb_d,2))
		folds_dict[nset]['axial_s'] = bisector_s
		folds_dict[nset]['axial_d'] = bisector_d
	'''
	By defining the generator limbs we can create two sets of measures with random normal distribuition to give a more "natural" feel to the dataset.
	'''

	
	
	
	return folds_dict	



def plane_plot(self,planes_dict,show_planes=1,show_poles=0,show_axial=0,show_hinge=0):
	
	set_color = ['r','g','b','k','m','c'] #plot with different colors depending on the set (0:red, 1:green, ...)
	
	self.plot.fig.clf()
	self.plot.ax = self.plot.fig.add_subplot(111, projection='stereonet')
	
	
	for sets in planes_dict:
		for i in range(len(planes_dict[sets]['s'])):
			if show_planes:
				self.plot.ax.plane(planes_dict[sets]['s'][i],planes_dict[sets]['d'][i],f'{set_color[sets]}-')
			if show_poles:
				self.plot.ax.pole(planes_dict[sets]['s'][i],planes_dict[sets]['d'][i],f'{set_color[sets]}o')
			if show_axial:
				self.plot.ax.plane(planes_dict[sets]['axial_s'], 
				                   planes_dict[sets]['axial_d'],f'{set_color[sets]}--')
			if show_hinge:
				self.plot.ax.pole(planes_dict[sets]['axial_s'], 
				                  planes_dict[sets]['axial_d'],f'{set_color[sets]}x')
		
	self.plot.ax.grid()
	self.plot.draw()
	


def random_focal_plot(self,color='k'):


	self.plot.fig.clf()
	
	for axis in [221,222,223,224]:
		self.plot.ax = self.plot.fig.add_subplot(axis, aspect='equal')
		self.plot.ax.axison = False

		
		s = np.random.randint(360)
		d = np.random.randint(90)
		r = np.random.randint(-90,181)
		beach = bb.beach([s,d,r],size=100,facecolor='k',linewidth=1)
		
		self.plot.ax.add_collection(beach)
		self.plot.ax.autoscale_view(tight=False, scalex=True, scaley=True)

	self.plot.draw()

# Convert CSV in dictionary with valid format such as {nset:{dd:[..],d:[..]},..}
def csv_convert(imported_path):
	import pandas as pd

	imported_data = pd.read_csv(imported_path)
	
	sets = imported_data['Set'].nunique() #take unique set values in dataframe
	
	nrows = len(imported_data.index)
	
	planes_dict = {x:{'dd':[],'d':[]} for x in range(sets)} #NOTE: not very good solution because it doesn't care about the file data. x always starts from 0. 
	#print(planes_dict)
	for _,v in imported_data.iterrows():
	
		dd,d,s = v.values
		#print(dd,d,s)
		planes_dict[s]['dd'].append(dd)
		planes_dict[s]['d'].append(d) 
		
	return planes_dict, nrows




	


