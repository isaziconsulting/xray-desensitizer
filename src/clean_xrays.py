import sys
import os
import warnings
import hashlib
import string
import gflags
from gflags import FLAGS
import progressbar
import pandas as pd
import Levenshtein as lv
from skimage import io
import crop_xray_vector as cxv
import OCR as ocr

# ignore warnings because ruins progress bar
warnings.filterwarnings("ignore", message="low contrast image")

# define input flags
gflags.DEFINE_boolean('debug', False, 'produces debugging output')
gflags.DEFINE_string('inpath', 'data', 'path to input data')
gflags.DEFINE_string('outpath', 'processed_data', 'path to output data')
gflags.DEFINE_enum('clean', 'inpaint', ['inpaint', 'mask'], 'type of image processing to perform')

def find_files(path):
    '''Recursively walks input directory and find all files within subdirectories.
    Arguments:
        path: Path to the input directory.
    Returns:
        all_files: All files as a path with corresponding subdirectories.
    '''
    all_files = []
    if os.path.isdir(path):
        subdirs = os.listdir(path)
        for subdir in subdirs:
            # recursively check next available directory until a file is found
            all_files += find_files(path+'/'+subdir)
        return all_files
    else:
        return [path]

def get_popular_string(all_strings):
    '''Finds most likely OCR output string based on string median calculations.
    Arguments:
        all_strings: All different OCR strings corresponding to the same x-ray image.
    Returns:
        Most Likely string.
    '''
    return lv.median(list(map(lambda x: x.upper(), all_strings)))

def get_patient_info(diff_imgs):
    '''Gets a unique hash of a patient name, the date that the x-ray was taken
    and the gender of the patient.
    Arguments:
        diff_imgs: Array of multiple copies of the same x-ray, each copy has a different type
        of image processing applied to it to affect the text in the image differently.
    Returns:
        patient_id: Unique hash of the patient name.
        xray_datetime: Date and time that the x-ray was taken.
        gender: Sex of the patient [M, F].
    '''
    patient_names = []
    patient_births = []
    xray_datetimes = []
    genders = []

    for img in diff_imgs:
        # run OCR
        patient_name, patient_birth, xray_datetime, gender = ocr.get_text_from_tesseract(img)
        patient_names += [patient_name]
        patient_births += [patient_birth]
        xray_datetimes += [xray_datetime]
        genders += [gender]
    # get the most likely string from all images
    patient_name = get_popular_string(patient_names)
    patient_birth = get_popular_string(patient_births)
    translator = str.maketrans('', '', string.punctuation)
    patient_birth = str(patient_birth).translate(translator)
    xray_datetime = get_popular_string(xray_datetimes)
    gender = get_popular_string(genders)
    # encrypt patient name
    to_encrypt = patient_name+patient_birth
    to_encrypt = to_encrypt.encode('utf-8')
    patient_id = hashlib.sha256(to_encrypt).hexdigest()[:20]

    return patient_id, xray_datetime, gender

def main(argv):
    try:
        # parse flags
        argv = FLAGS(argv)
    except gflags.FlagsError as e:
        print('%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS))
        sys.exit(1)
    if FLAGS.debug:
        print('non-flag arguments:', argv)

    # retrieve all the files to be processed
    all_files = find_files(FLAGS.inpath)
    # define pandas dataframe
    df = pd.DataFrame(columns=('patientID', 'xrayDateTime', 'gender', 'path'))

    pbar = progressbar.ProgressBar(maxval=len(all_files))
    pbar.start()

    for i, name in enumerate(all_files):
        # run image processing
        new_image, all_images = cxv.run_system(name, FLAGS.clean)
        write_name = name.replace(FLAGS.inpath, FLAGS.outpath)
        split_name = write_name.rsplit('/', 1)[0]
        if not os.path.exists(split_name):
            os.makedirs(split_name)
        io.imsave(write_name, new_image)
        # run OCR for hash
        patient_id, xray_datetime, gender = get_patient_info(all_images)
        df.loc[i] = [patient_id, xray_datetime, gender, write_name]
        # update progress bar
        pbar.update(i)
    pbar.finish()
    df.to_csv(FLAGS.outpath+'/labelled_info.csv')

if __name__ == '__main__':
    main(sys.argv)
