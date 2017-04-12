<div align="center">
  <img src="http://www.isaziconsulting.co.za/images/Logo3.png"><br><br>
</div>

-----------------

The x-ray desensitization tool was developed as a means to increase the inflow of x-ray data from hospitals without breaching patient confidentiality. For more information please refer to our [blog post]().

-----------------

## Requirements

The code base was developed in conjunction with a [Docker container](https://cloud.docker.com/swarm/isazi/repository/docker/isazi/xray-desensitizer/general) in order to avoid dependecy problems. If you would prefer to not use the Docker container the following are required:

* [Tesseract 4.0 (with LSTM)+](https://github.com/tesseract-ocr/tesseract/wiki/4.0-with-LSTM)
* OpenCV 3.2.0+
* Python 3.5.2+
* Python libraries
    * numpy
    * pandas
    * Pillow
    * progressbar33
    * pytesseract
    * python-gflags
    * python-Levenshtein
    * scikit-image
    * scipy
    * python-opencv

-----------------

## Usage

When using both the Docker image and the plain source code it is necessary to have all the x-rays in a single folder, the code will recreate another folder of processed x-rays with the same subdirectory structure as the input folder.

### With Docker container

The Docker container has been built to clone the repository and execute the code when run. A simple bash script, *desensitizer.sh*, was made to provide an easier interface for entering the path to the input folder and the path to the output folder. So running `bash desensitizer.sh` and following the on-screen prompts is all that is required.

### Without Docker container

`clean-xrays.py` functions as the API, it has the following parameters.

* --inpath: path to input data folder.

* --outpath: path to output data folder.

* --clean: type of image processing to perform.

    * [default] inpaint: fill in the image where the text was, it will appear as if the text never existed.

    * mask: mask off where the text was, this will appear as black blocks.

-----------------
