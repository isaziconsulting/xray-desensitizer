import numpy as np
from skimage import io
from skimage.color import rgb2grey
import cv2

# the RBG vector that we are testing against
#######################################################################
# NOTE: This would change if the main colour that you are looking for #
# is not yellow, however it does infact detect all colours it's just  #
# better as using the dominant colour.                                #
#######################################################################
TEST_YELLOW = np.array([255, 245, 149])
# some value greater that 0 so that we don't divide by zero
EPSILON = 0.001

def get_projection_mask_matrix(test_img):
    '''Get a mask of the projection of the test RGB onto the original image.
    Arguments:
        test_img: The image to project the RGB vector onto.
    Returns:
        mask: Mask of RGB vector projected onto image.
    '''
    test_red = np.array(test_img[:, :, 0], np.float32)
    test_green = np.array(test_img[:, :, 1], np.float32)
    test_blue = np.array(test_img[:, :, 2], np.float32)
    norm_test = np.sqrt(test_red**2 + test_green**2 + test_blue**2)
    norm_test[norm_test == 0] = EPSILON
    norm_yellow = np.linalg.norm(TEST_YELLOW)
    dot_prod = np.dot(TEST_YELLOW[0], test_red) + np.dot(TEST_YELLOW[1], test_green) + np.dot(TEST_YELLOW[2], test_blue)

    mask = dot_prod/(norm_test * norm_yellow) * 255
    return np.array(mask, np.uint8)

def get_mask(img):
    '''Performs different morphological operations on the image and returns
    each result in a vector of images.
    Arguments:
        img: Original x-ray image.
    Returns:
        closing: Result after performing closing operation on the projection mask
        with threshold at 0.
        closing_ocr: Result after performing closing on the colour text only,
        with threshold at 254.
        dilated_ocr: Result after performing dilation on the closing_ocr image.
    '''
    mask = get_projection_mask_matrix(img)
    closing_ocr = mask.copy()
    # 245-250 is where all the gray sits
    mask[np.where(np.logical_and(mask > 245, mask < 250))] = 0
    # perform closing on mask
    mask[mask > 0] = 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    # select only values that are yellow
    closing_ocr[closing_ocr < 254] = 0
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    closing_ocr = cv2.morphologyEx(closing_ocr, cv2.MORPH_CLOSE, kernel, iterations=1)
    closing_ocr[closing_ocr > 0] = 255
    # dilate mask
    dilated_ocr = closing_ocr.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    dilated_ocr = cv2.dilate(dilated_ocr, kernel, iterations=1)
    dilated_ocr = cv2.morphologyEx(dilated_ocr, cv2.MORPH_OPEN, kernel, iterations=1)

    return [closing, closing_ocr, dilated_ocr]

def hide_names_mask(mask):
    '''Simple thresholding still has the text as visible, so this function
    dilates the image to the point where the original text is unrecognisable.
    Arguments:
        mask: Image obtained from projection.
    Returns:
        mask: Masked image after performing a dilation on the mask.
    '''
    # expand the mask so it completely hides the names
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    return cv2.dilate(mask, kernel, iterations=2)

def get_extracted_img(no_text):
    '''Crops only the x-ray from the image.
    Arguments:
        no_text: Image that now has the text removed.
    Returns:
        new_image: Croped x-ray image.
    '''
    # find the largest box and extract it
    _, contours, _ = cv2.findContours(np.uint8(255*rgb2grey(255*np.uint8(no_text > 15))), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    biggestContourIndex = np.argmax(list(map(cv2.contourArea, contours)))

    x_min, y_min, w, h = cv2.boundingRect(contours[biggestContourIndex])
    x_max = x_min + w
    y_max = y_min + h
    new_image = no_text[y_min:y_max, x_min:x_max]
    return new_image

def get_only_text(mask, raw_img):
    '''Masks off everything from the original image other than text.
    Arguments:
        mask: Mask that highlights text.
        raw_img: Original image.
    Returns:
        raw_img: Original image with text masked off.
    '''
    # extract only the text (in RGB) from the image
    mask = mask/255
    for i in range(3):
        raw_img[:, :, i] = raw_img[:, :, i] * mask
    return raw_img

def run_system(img_name, proc_type='inpaint'):
    '''Wraps all functionality for image processing into a single function.
    Arguments:
        img_name: Path to image of interest.
        proc_type: Type of processing to perform.
    Returns:
        new_image: Cropped and processed image.
        all_images: Vector of all images to be used for OCR.
    '''
    img = io.imread(img_name)
    # get image mask
    all_images = get_mask(img)
    # inpaint image or masking out the text
    if proc_type == 'inpaint':
        no_text = cv2.inpaint(img, all_images[0], 3, cv2.INPAINT_NS)
    elif proc_type == 'mask':
        all_images[0] = hide_names_mask(all_images[0])
        all_images[0] = np.array((255 - all_images[0])/255, np.uint8)
        no_text = img.copy()
        no_text[:, :, 0] = np.array(no_text[:, :, 0] * all_images[0], np.uint8)
        no_text[:, :, 1] = np.array(no_text[:, :, 1] * all_images[0], np.uint8)
        no_text[:, :, 2] = np.array(no_text[:, :, 2] * all_images[0], np.uint8)
    # get biggest blob
    new_image = get_extracted_img(no_text)
    yellow_img = get_only_text(all_images[1], img)
    all_images[0] = yellow_img

    return new_image, all_images
