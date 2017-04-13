Anyone who has ever attempted to apply data science in the medical industry will understand the amount of red tape that one needs to go through in order to obtain data. Although understandable, this can really slow down the progression of a project, especially when large quantities of data are required.

We recently encountered this problem when trying to apply deep learning to x-ray images. Freely available datasets are few and far between, which meant we needed to gather data directly from local hospitals. Our first attempt at this took about three weeks for us to get a small subset back. This delay was primarily due to the fact that the x-rays needed to be completely anonymized before they could be handed over to us. As these kinds of delays are obviously impractical we decided to develop a desensitization tool that could be deployed to the hospital so that we could streamline this process.

# The Data

The raw data that we were receiving would be an x-ray arbitrarily placed on a black background with the sensitive patient information written across the x-ray in a yellow colour, much like the image seen below.

*NOTE: The image below was obtained from the [Montgomery County chest x-ray set](http://archive.nlm.nih.gov/repos/chestImages.php) and fake text was imposed onto the image*

<center><img src="data/sensitive.jpg" alt="X-Ray containing sensitive information" style="width: 650px;"/></center>

# The Desensitization Tool

The desensitization tool had two primary functions, firstly to remove all sensitive patient information and secondly to OCR this information to obtain a unique hash of the patient's name as well as other metadata.

## Removing sensitive information

Localization of the text had to be 100% accurate in order to make the tool feasible. To achieve this we obtained the RGB vector for the yellow colour of the text and took the dot product of each pixel in the image with this vector in order to obtain a 'degree of yellowness' for each pixel. When plotting a histogram of the output it was clear which values corresponded to the image and which corresponded to the text. Thresholding these outputs produced the following result. An interesting thing to note is that this method was suitable for determining all colour from gray as it was able to detect the red text as well. 

<center><img src="data/proj_mask.png" alt="Mask after RGB projection" style="width: 650px;"/></center>