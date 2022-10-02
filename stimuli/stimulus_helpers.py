
# Helper functions for generating attention video stimuli
# created by Kirsten Ziman, 9/13/22

# Note: functions not created by Kirsten Ziman cite the original source
#       these functions begin at line 

import os
from matplotlib import pyplot as plt
from scipy import ndimage
import seaborn as sb
import pandas as pd
import imageio
import math
import numpy as np
import ffmpeg
import random
import glob
import csv

def rename_df(splitso, this_version):
    '''
    INPUT:
    splitso      - pandas dataframe containing full gaze data from one subject for one image
    this_version - version of the image list this data is from
    
    OUTPUT:
    splitso      - original dataframe but with appropriately renamed columns for easy analysis
    '''
    
    thirteen = False; 

    if 13 in splitso.columns:
        for x in list(splitso[13].unique()):
            if type(x) == str:
                if '.bmp' in x:
                    thirteen = True

    if thirteen == True:
        splitso = splitso.rename(columns={0: "Time", 1: "Type", 2:"Trial", 3:"L POR X [px]",
                                          4:"L POR Y [px]", 5:"R POR X [px]", 6:"R POR Y [px]",
                                          7:"Timing", 8:"Pupil Confidence", 9:"L Plane", 10:"R Plane",
                                         11:"L Event Info", 12:"R Event Info", 13:"Stimulus"})

    elif thirteen == False:
        splitso = splitso.rename(columns={0: "Time", 1: "Type", 2:"Trial", 3:"L POR X [px]",
                                          4:"L POR Y [px]", 5:"R POR X [px]", 6:"R POR Y [px]",
                                          7:"Timing", 8:"Pupil Confidence", 9:"L Plane", 10:"R Plane",
                                         13:"L Event Info", 14:"R Event Info", 15:"Stimulus"})
    else:
        print('Incoherent list version number!')
        
    return(splitso)


def make_splitso(sub, dat_string, this_list, this_version):
    '''
    INPUT:
    dat_string - path to trial data
    
    OUTPUT:
    splitso    - pandas dataframe containing desired trial data w/ appropriate column names, float values, etc.
    '''
    
    df         = pd.read_csv(dat_string, sep=" ", skiprows=None, skipinitialspace=True, skip_blank_lines=True, header=41)
    splitso    = df['Time\tType\tTrial\tL'].str.split('\t', expand=True)
    splitso    = rename_df(splitso, this_version)[1:]
    
    splitso['L POR X [px]'] = splitso['L POR X [px]'].astype(float)
    splitso['L POR Y [px]'] = splitso['L POR Y [px]'].astype(float)
    splitso['subject']      = sub
    splitso['list']         = this_list
    splitso['version']      = this_version
    
    return(splitso)
    

def get_gaze(sub, this_list, this_version, image):
    '''
    INPUTS:
    sub          - string indicating subject ID (example: 'pp151')
    this_list    - int indicating which List the image is from (1, 2, or 3)
    this_version - int indicating which Version of this_list the data is from (1 or 2)
    
    OUTPUTS:
    gaze_data    - df containing sub's full gaze data for image 
    '''

    subdir     = '../Free_viewing/List'+str(this_list)+'_ALL/'+sub+'/eye'
    eye_trials = os.listdir(subdir)
    null       = 0

    for trial in eye_trials:
        if trial!='.DS_Store' and trial[-3:]!='csv':

            dat_string = subdir+'/'+trial
            splitso    = make_splitso(sub, dat_string, this_list, this_version)

            if 'Stimulus' in splitso.columns:
                if splitso[splitso['Stimulus']==image].shape[0]>0:
                    free_view = splitso[splitso['Stimulus']==image]
                    null+=1
            else:
                if warning_counter == 0:
                    print('No stimulus column in the df')
                    print(sub)
                    print(this_list)
                    print(this_version)
                    #print(splitso.head())

    if null==0:
        print("Reportedly, "+sub+" has no values in df for this stimulus: "+image)
        print(sub)
        print(this_list)
        print(this_version)
        free_view = []
        print(splitso.head())
        
    return(free_view)


def get_fixies(free_view):
    """
    INPUT:
    free_view  - gaze data from one subject for one image
    
    OUTPUT:
    fixie_list - list of ints of length #-of-fixations
               - the value of each int reflects which chunk the corresponding fixation point belongs to
    """
    
    events = list(free_view['L Event Info'])
    fixation_chunk = 1 
    fixie_list = []

    for idx,x in enumerate(events[:-1]):
        if x == 'Fixation':
            fixie_list.append(fixation_chunk)
            if events[idx+1] != 'Fixation':
                fixation_chunk += 1
    
    if events[-1] == 'Fixation':
        if events[-2] == 'Fixation':
            fixie_list.append(fixation_chunk)
        else:
            fixie_list.append(fixation_chunk+1)
                
    return fixie_list


def check_fix_numbers(fixie_list, free_view):
    '''
    INPUT:
    fixie list - output of get_fixies function
    free_view  - output of get_gaze function
    
    OUTPUT:
    value      - boolean - True if fixie_list is correct length
    '''
    for x,y in zip(fixie_list, fixation_data):
        if len(x)!=y[y['L Event Info']=='Fixation'].shape[0]:
            value = False
        else:
            value = True
    return(value)

def make_the_dicts(free_view):
    '''
    INPUT: 
    splitso - pandas dataframe containing gaze data from one subject for one image
    
    OUTPUT:
    dict    - dictionary format of data and image to pass into plotting functions
    '''
    
    xs = free_view[free_view['L Event Info']=='Fixation']['L POR X [px]'] 
    ys = free_view[free_view['L Event Info']=='Fixation']['L POR Y [px]'] 
    tuple_list = []
    
    for x,y in zip(xs,ys):
        tuple_list = tuple_list+[(np.rint(x),np.rint(y))]
        the_dict = {'image':free_view['Stimulus'][1], 'fixations': tuple_list, 'subject':free_view['subject'].unique(),'list':free_view['list'].unique(), 'version':free_view['version'].unique()} 
        
    return the_dict

def get_addin(q):
    '''
    INPUT:
    q - int indicating the number of the image that's being generated
    
    OUTPUT:
    addin - string to include in the jpeg filename so that files/filenames are ordered correctly for video compilation
    '''
    
    addin = '_'
    
    if q<10:
        addin = addin+'00'
    elif q>=10 and q<100:
        addin = addin+'0'
        
    return(addin)

def get_framerate():
    '''
    OUTPUTS: frame_rate - int - optimal framerate to produce 3 second video, rounded down to the nearest int
    '''
    num_images = 0
    for img in os.listdir('.'):
        if img[-3:]=='jpg':
            num_images+=1

    # total frames / total seconds  --> frames per second
    frame_rate = math.floor(num_images/3)
    
    return(frame_rate)

def remove_jpegs():
    '''
    removes all jpegs in current directory
    '''
    for file_name in os.listdir('.'):
        if file_name.endswith('.jpg'):
            os.remove(file_name)

def first_bounds_update(x1_vals,y1_vals,b):
	'''
	INPUTS:
	x1_vals - list of length 2 
				  - first list item: smallest x val encountered so far
				  - second list iftem: largest x val encountered so far

	y1_vals - list of length 2 
				  - first list item: smallest y val encountered so far
				  - second list iftem: largest y val encountered so far

	b       - tuple - new tuple to compare with current values

	OUTPUTS:
	x1_vals - list of length 2 
				  - first list item: smallest x val encountered so far, given b
				  - second list iftem: largest x val encountered so far, given b

	y1_vals - list of length 2 
				  - first list item: smallest y val encountered so far, given b
				  - second list iftem: largest y val encountered so far, given b

	'''
	new_x = b[0]

	if new_x < x1_vals[0]:
		x1_vals[0] = new_x

	if new_x > x1_vals[1]:
		x1_vals[1] = new_x

	new_y = b[1]

	if new_y < y1_vals[0]:
		y1_vals[0] = new_y

	if new_y > y1_vals[1]:
		y1_vals[1] = new_y

	return(x1_vals, y1_vals)


def one_centered(x1_vals, y1_vals):
	'''
	INPUTS:
	x1_vals - list of length 2 
					- first list item: smallest x val in first attention hotspot
					- second list iftem: largest x val in first attention hotspot

	y1_vals - list of length 2 
				  - first list item: smallest y val in first attention hotspot
				  - second list iftem: largest y val in first attention hotspot

	OUTPUT:
	one_centered - string - describes whether first hotspot is at screen-center
	'''

	DISPLAY_SIZE = (1050, 1680)

	center_x = 1050/2
	center_y = 1680/2

	# print(x1_vals)
	# print(y1_vals)

	if center_x>x1_vals[0] and center_x<x1_vals[1]:
		x_cent=True
	else:
		x_cent=False

	if center_y>y1_vals[0] and center_y<y1_vals[1]:
		y_cent=True
	else:
		y_cent=False

	if x_cent and y_cent:
		one_centered='T'

	elif x_cent==True and y_cent == False:
		one_centered = 'x_only'

	elif x_cent==False and y_cent == True:
		one_centered = 'y_only'

	elif x_cent==False and y_cent == False:
		one_centered = 'F'

	else:
		one_centered = 'ERROR'

	return(one_centered)


def movie_maker(fixations, dictionary, this_list, this_version, stim_type, isolated=False):
    '''
    INPUTS:
    
    fixations  - pandas dataframe containing only fixation data from one subject viewing one image
    dictionary - dictionary containing two keys, one with the image name and one with the fixaiton coordinates 
    stim_type  - string describing the type of attention stimulus to make: veridical / scrambled / mismatched / reversed
    isolated   - boolean describing whether the attention will be isolated (True) or be overlaid on an image (False)
            
    OUTPUTS: 
    
    technically, none
    
    This will create and save two files: 
    - mp4 video of the attention video stimulus
    - csv containing video metadata
        - # of attention chunks (num_chunks)
        - order of attention chunks (order)
        - image filename (dictionary['image'])
        - subject ID (dictionary['subject'])
    '''
    
    # This function can make veridical and scrambled attention spotlight videos, isolated or overlaid on an image

    lengths = []; movie_frames = []; total_counter = 0
    order   = list(set(fixations))
    num_chunks = len(order)

    if len(order)>2:

        # scramble order for scrambled stimulus
        if stim_type=='scrambled':
            while order == list(range(1, len(order)+1)):
                remainder = order[1:]
                np.random.shuffle(remainder)
                new_list = [order[0]] + list(remainder)
                order = new_list

        # record how many chunks stay in the same place (besides the first one), if any
        number_same = sum(x == y for x, y in zip(order, list(range(1, len(order)+1))))-1
            
        # for each fixation chunk 
        for x in order:
    
            length_counter = 0; tuple_list = []; total_list = []

            # for first chunk, collect the largest and smallest x and y vals
            if x==1:
            	x1_vals=[100000000000,0]; y1_vals=[100000000000,0]
            	# initialize very high and very low values, respectively

            # for each item in fixie chunk list AND each tuple
            for a,b in zip(fixations, dictionary['fixations']):

                # if item from fixie chunk list is the number from first for statement:
                if a == x:
                    tuple_list.append(b)
                    total_counter += 1
                    total_list.append(total_counter)
                    if x==1:
                    	x1_vals,y1_vals = first_bounds_update(x1_vals,y1_vals,b)
            
            # determine if first hotspot contains center of screen
            first_centered   = one_centered(x1_vals, y1_vals)
            reverse_centered = one_centered(y1_vals, x1_vals)

            # pass into plotting function
            plot_heatmap({'image':dictionary['image'], 'fixations':tuple_list}, 
                         filename='/Users/kirstenziman/Downloads/images_with_borders/Images_resized_greyborders/List'+str(this_list)+'/' + dictionary['image'], 
                         alpha=.6, cmap="Greys_r", clean=False, isolated=isolated, other=None, l=this_list)
            
            # save jpegs    
            for q in total_list:
                addin = get_addin(q)
                plt.savefig(dictionary['image']+addin+str(q)+'.jpg')

        # determine frame rate given number of images
        framerate = get_framerate()

        if framerate!=0:
            ending = '_'+dictionary['subject'][0]+'_L'+str(this_list)+'_V'+str(this_version)+'_'+stim_type+'_freeview_iso'+str(isolated)

        # compile and save video
            (
            ffmpeg
            .input('*.jpg', pattern_type='glob', framerate=framerate)
            .output(dictionary['image']+ending+'.mp4')
            .run()
            )
            
            # remove leftover jpeg images
            remove_jpegs()

        else:
            print('framerate is zero for '+dictionary['image'])

            for file_name in os.listdir('.'):
                if file_name.endswith('.jpg'):
                    os.remove(file_name)

        meta = pd.DataFrame({'image':dictionary['image'],'subject':dictionary['subject'],'num_chunks':num_chunks, 'order':[order], 'center_first':str(first_centered), 'center_first_reverse':str(reverse_centered), 'chunks_same': number_same, 'proportion_same':number_same/(len(order)-1), 'x1_vals':[x1_vals], 'y1_vals':[y1_vals]})

        meta.to_csv(dictionary['image']+ending+'.csv')

    else:
        print('len(k) <= 2: '+dictionary['image'])


########################################################################
# the functions below are from : https://didec.uvt.nl/pages/download.html
# (see the second download link under "Images" section)
# any changed lines to the original functions have been commented "#KZ"
########################################################################


DISPLAY_SIZE = (1050, 1680)

def get_coords(entry):
    """
    Helper function to get coordinates from an entry.
    Own code.
    """
    x = round(float(entry['L POR X [px]']))
    y = round(float(entry['L POR Y [px]']))
    return x,y


def get_fixations(entries, remove_out_of_bounds=True):
    """
    Get the fixations from the BeGaze file, and return them in the PyGaze format.
    Own code.
    """
    coords = [get_coords(entry) for entry in entries
                                if entry['L Event Info'] == 'Fixation'
                                and entry['R Event Info'] == 'Fixation']
    if remove_out_of_bounds:
        height, width = DISPLAY_SIZE
        coords = [(x,y) for x,y in coords if x < width and y < height]
    return coords


def read_eye_data(filepath, remove_out_of_bounds=True):
    """
    Read the BeGaze data.
    Own code.
    """
    with open(filepath) as f:
        # There's a lot of lines that are just unnecessary..
        for i in range(41):
            _ = next(f) # Skip line
        reader = csv.DictReader(f, delimiter='\t')
        entries = list(reader)
        # The first entry is not a real entry but a message about the stimulus.
        message = entries[0]
        image = entries[0]['L POR X [px]'].split()[-1]
        del entries[0]
        return dict(image=image, fixations=get_fixations(entries, remove_out_of_bounds))


def buildFixMap(fixations, doBlur=True, sigma=19, display=(1050, 1680)):
    """
    Function to build a fixation map.
    Based on salicon.py
    """
    sal_map = np.zeros(display)
    for x,y in fixations:
        if y<=1050.00 and x<=1680.00:
            sal_map[int(y)][int(x)]=1
            # KZ #sal_map[y][x] = 1 
        else:
            print('one gazepoint detected out of bounds')
    if doBlur:
        sal_map = ndimage.filters.gaussian_filter(sal_map, sigma)
        sal_map -= np.min(sal_map)
        sal_map /= np.max(sal_map)
    return sal_map


def clean_heatmap(heatmap):
    """
    Remove numbers below the mean to make the visualization clearer.
    Own code.
    """
    lowbound = np.mean(heatmap[heatmap>0])
    heatmap[heatmap<lowbound] = np.NaN
    return heatmap


def CC_score(gtsAnn, resAnn):
    """
    Computer CC score. A simple implementation
    From the SALICON codebase.
    
    :param gtsAnn : ground-truth fixation map
    :param resAnn : predicted saliency map
    :return score: int : score
    """
    fixationMap = gtsAnn - np.mean(gtsAnn)
    if np.max(fixationMap) > 0:
        fixationMap = fixationMap / np.std(fixationMap)
    salMap = resAnn - np.mean(resAnn)
    if np.max(salMap) > 0:
        salMap = salMap / np.std(salMap)
    
    return np.corrcoef(salMap.reshape(-1), fixationMap.reshape(-1))[0][1]


# KZ added "isolated attention" option 
#def plot_heatmap(data, filename='test.pdf', alpha=0.7, cmap='jet', clean=True):
def plot_heatmap(data, filename='test.pdf', alpha=0.7, cmap='jet', clean=True, isolated=False, other=None, l=1):
    """
    Plot heatmap.
    Mostly modified from PyGaze.
    """
    # Load data
    image      = data['image']
    image_path = '/Users/kirstenziman/Downloads/images_with_borders/Images_resized_greyborders/List '+str(l)+'/'+data['image'] # IMAGE_PATHS[image]
    #KZ update from ndimage to imageio #image_data = ndimage.imread(image_path)
    image_data = imageio.imread(image_path)
    heatmap    = buildFixMap(data['fixations'])
    # Remove haze.
    if clean:
        heatmap = clean_heatmap(heatmap)
    
    # Matplotlib.
    # Borrows heavily from from Edwin Dalmaijer's `gazeplotter.py` script, from the PyGaze codebase.
    dpi = 100
    display_size = heatmap.shape
    figsize = (display_size[1]/dpi, display_size[0]/dpi)
    fig = plt.figure(figsize=figsize, dpi=dpi, frameon=False)
    ax = plt.Axes(fig, [0,0,1,1])
    ax.set_axis_off()
    fig.add_axes(ax)
    
    if isolated == False and other == None:
        ax.imshow(image_data)
        # KZ moved ax.imshow(image_data) into if statement for "isolated attention" option
    
    elif other != None:
        image_data= imageio.imread(other)
        ax.imshow(image_data)
        print(other)
        
    ax.imshow(heatmap, cmap=cmap, alpha=alpha)
    #KZ commented out: #fig.savefig(filename)