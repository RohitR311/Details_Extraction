# Details_Extraction
A basic image processing task to detect and enter details from images or pdf into an excel or csv file

## Initial setup:

The optimal size of images was determined by taking the mean of the heights and widths of all the images present in the “images” directory.
This optimal size is further used to resize images while looping through all the images.
If the “pdf” parameter is set to True in the “create_file” method then each page of input pdf is converted to an image or else the “images” directory is used as default.
The preferred format of “.csv” or “.xlsx” needs to be specified as a parameter as well.

## Extracting textual information:

The individual images are read, resized and converted to grayscale while looping.
The grayscale images are thresholded using OTSU’s method as it is essential to perform contour detection.
A rectangular kernel is specified of optimal size arrived through trial and error process. This kernel is used to detect the text individually to perform dilation.
The thresholded images are dilated according to the kernel specified. This step is performed so as to improve the accuracy of the contour detection.
Contour detection returns an array of contours.
These contours are looped through and a condition is specified so as to consider only the contours relevant to the task. The condition being the area of the contour.
The rectangular coordinates of each contour are retrieved and the image is cropped using these coordinates.
The cropped image is then converted into string using the “pytesseract” tool used for OCR.
The textual data is then appended to a list and the list is returned for further processing.

## Extracting symbol code:

The symbol images in the “symbols” directory are resized to an optimal size and stored in a new directory “resized_symbols” so as to efficiently detect them in the images or pdf specified. 
These symbol images are then looped through and each symbol image is read and compared with the grayscale version of the original image using template matching.
OpenCV’s matchTemplate checks if a given image is present within another image and returns an array of values.
The max value from this array specifies the likelihood or confidence of the symbol being present in the grayscale image.
A confidence threshold is specified through trial and error. A value greater than this threshold is accepted and the symbol code i.e the name of the image is appended to an empty list.
This list is then joined and returned using “.join()”.

## Exporting file:

All the textual details obtained from the “pytesseract” tool as well as the symbol code are appended to an empty list.
This list is then converted to a data frame using the pandas library.
As the data frame created is quite flexible it can be exported to the file format specified in “create_file” method i.e either “.csv” or “.xlsx”.
This concludes the “details extraction” task.
