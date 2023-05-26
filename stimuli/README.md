# Stimulus Generation 

In order to generate the stimuli from scratch, you will need to download the images and eye tracking data from the Dutch Imaging Description and Eye Tracking Corpus: https://didec.uvt.nl/pages/download.html

The data we used to generate our stimuli were as follows (accessed 7/2022-4/2023):

- Images: Downloaded images from "Download the images here." under the Images section of the DIDEC site. Utilized the images in `images_with_borders/Images_resized_greyborders`
- Eye tracking data: Download "The entire corpus" under the Download section of the DIDEC site. Utilize eye tracking data in `DIDEC_entire_corpus/Free_viewing`

Note that the image and eye tracking data are split into directories by list number and version number. In some cases, for convenience, we grouped all of the data into a single directory for stimulus creation. You may need to rearrange the data within directories and update filepaths in the stimulus generation code appropriately.

Note also that no stimulus generation code is provided for experiment 8; it utilizes the same video stimuli as Experiment 1 in the context of a different experimental paradigm.
