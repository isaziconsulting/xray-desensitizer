import string
from PIL import Image
import pytesseract

#############################################################################
# NOTE: The format of the text layout in the x-ray is very important for    #
# returning the correct text, if the format is not exactly the same as that #
# provided in the sample image then please adjust the values below.         #
#############################################################################
def get_text_from_tesseract(img):
    '''Runs tesseract OCR on an image and segments returns.
    Arguments:
        img: Image to perform OCR on.
    Returns:
        patient_name: Name of patient.
        birth: Date of birth of patient.
        xray_datetime: Date and time the x-ray was taken.
        gender: Sex of patient.
    '''
    img = Image.fromarray(img)
    translator = str.maketrans('', '', string.punctuation)
    raw_text = pytesseract.image_to_string(img).translate(translator).replace(" ", "")
    raw_text = raw_text.split("\n")
    raw_text = list(filter(lambda x: x != '', raw_text))
    patient_name = raw_text[0]
    # might not receive enough text
    try:
        birthGender = raw_text[2]
    except:
        birthGender = "UnkU"
    birth, gender = birthGender[:-1][-9:], birthGender[-1:]
    xray_datetime = raw_text[-1][:-4]

    return patient_name, birth, xray_datetime, gender
