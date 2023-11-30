# Stimulus Generation 

In order to generate the stimuli from scratch, you will need to download the images and eye tracking data from the Dutch Imaging Description and Eye Tracking Corpus: https://didec.uvt.nl/pages/download.html

The data we used to generate our stimuli were as follows (accessed 7/2022-4/2023):

- Images: Downloaded images from "Download the images here." under the Images section of the DIDEC site. Utilized the images in `images_with_borders/Images_resized_greyborders`
- Eye tracking data: Download "The entire corpus" under the Download section of the DIDEC site. Utilize eye tracking data in `DIDEC_entire_corpus/Free_viewing`

Note that the DIDEC image and eye tracking data are split into directories by list number and version number. In some cases, for convenience, we grouped all of the data into a single directory for stimulus creation. You may need to rearrange the data within directories and update filepaths in the stimulus generation code appropriately. 

If you run the stimulus generation code in each experiment folder, you will generate video stimuli with pseudo-randomly selected viewer-image pairs. To remake the exact stimuli used in our experiments, pass in a dataframe selecting the same image-viewer pairs as indicated by the filenames in the corresponding stimulus zip file (e.g. `../experiments/experiment_1/STIM_SET_1.zip`). 

Note  that no stimulus generation code is provided for experiment 8; it utilizes the same video stimuli as Experiment 1 in the context of a different experimental paradigm. Note also that stimuli for Experiments 1 and 2 were compressed by our experiment display system (so there is no video compression code in `experiments_1_and_2`); videos for subsequent experiments (3-8) were reduced beforehand via the code provided in the respective directories.

For questions regarding stimulus generation, please contact: kz0108@princeton.edu or kirstenkmbziman@gmail.com
