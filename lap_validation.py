from cv2 import cv2
import pytesseract
import re

def lap_basic_processing(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, shift):
	temp=y_lap
	
	if shift==1:
		y_lap=y_lap-vertical_shift_phone#I still need to make sure it work with multiple resolution, this is based on a single sample for 936p video
	
	sub_image = frame[y_lap:y_lap+h_lap, x_lap:x_lap+w_lap]
	gray = cv2.cvtColor(sub_image, cv2.COLOR_BGR2GRAY)
	gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
	
	
	data = pytesseract.image_to_string(gray, lang='eng', config='--psm 10').lower()
	data_lap_list=re.findall(r'\d+', data)
	
	y_lap=temp
	
	print('lap_basic_processing : ')
	print(data)
	
	return data_lap_list


	
def lap_alternative_image_processing(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, shift): 
	temp=y_lap
	
	if shift==1:
		y_lap=y_lap-vertical_shift_phone#I still need to make sure it work with multiple resolution, this is based on a single sample for 936p video
	
	sub_image = frame[y_lap:y_lap+h_lap, x_lap:x_lap+w_lap]
	gray = cv2.cvtColor(sub_image, cv2.IMREAD_GRAYSCALE)
	gray[gray < 240] = 0
	
	scaled = cv2.resize(gray, (0,0), fx=10, fy=10, interpolation = cv2.INTER_CUBIC)
	
	pre_processed = scaled

	data = pytesseract.image_to_string(pre_processed, lang='eng', config='--psm 6 --oem 3 tessedit_char_whitelist=0123456789').lower()
	data_lap_list=re.findall(r'\d+', data)
	
	y_lap=temp
	
	print('lap_alternative_processing : ')
	print(data)
	
	return data_lap_list	
	
	
	
def lap_alternative_image_processing2(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, shift):#improvement for day time processing
	temp=y_lap
	
	if shift==1:
		y_lap=y_lap-vertical_shift_phone#I still need to make sure it work with multiple resolution, this is based on a single sample for 936p video
	
	sub_image = frame[y_lap:y_lap+h_lap, x_lap:x_lap+w_lap]
	gray = cv2.cvtColor(sub_image, cv2.COLOR_BGR2GRAY)

	# ksize
	ksize = (2, 2)
	  
	# Using cv2.blur() method 
	gray = cv2.blur(gray, ksize)

	gray = cv2.resize(gray, None, fx=6, fy=6, interpolation=cv2.INTER_CUBIC)
	gray[gray < 190] = 0

	data = pytesseract.image_to_string(gray, lang='eng', config='digits').lower()
	data_lap_list=re.findall(r'\d+', data)
	
	y_lap=temp
	
	print('lap_alternative_processing 2 : ')
	print(data)
	#cv2.imshow("gray", gray)
	#cv2.waitKey(0)
	
	return data_lap_list


def lap_alternative_image_processing3(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, shift):#backup
	temp=y_lap
	
	if shift==1:
		y_lap=y_lap-vertical_shift_phone#I still need to make sure it work with multiple resolution, this is based on a single sample for 936p video
	
	sub_image = frame[y_lap:y_lap+h_lap, x_lap:x_lap+w_lap]
	gray = cv2.cvtColor(sub_image, cv2.IMREAD_GRAYSCALE)
	gray[gray < 240] = 0
	
	scaled = cv2.resize(gray, (0,0), fx=10, fy=10, interpolation = cv2.INTER_CUBIC)
	
	pre_processed = scaled

	data = pytesseract.image_to_string(pre_processed, lang='eng', config='--psm 6 --oem 3 tessedit_char_whitelist=0123456789').lower()
	data_lap_list=re.findall(r'\d+', data)
	
	y_lap=temp
	
	print('lap_basic_processing : ')
	print(data)
	
	return data_lap_list	
	
def lap_alternative_image_processing4(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, shift):#not currently used
	temp=y_lap
	
	if shift==1:
		y_lap=y_lap-vertical_shift_phone#I still need to make sure it work with multiple resolution, this is based on a single sample for 936p video
	
	sub_image = frame[y_lap:y_lap+h_lap, x_lap:x_lap+w_lap]
	gray = cv2.resize(sub_image, None, fx=6, fy=6, interpolation=cv2.INTER_LINEAR)
	gray[gray < 190] = 75#245 marchais bien

	data = pytesseract.image_to_string(gray, lang='eng', config='digits').lower()
	data_lap_list=re.findall(r'\d+', data)
	
	y_lap=temp
	
	print('lap_basic_processing : ')
	print(data)
	
	return data_lap_list
	
	
def lap_list_too_big(data_lap_list, current_lap, result_list_too_big):
	if len(data_lap_list)>2:
		y=0
		data_isnumeric=0
		while y < len(current_lap):
			if data_lap_list[y].isnumeric :
				print('data_lap_list isnumeric')
				data_isnumeric=data_isnumeric+1
			y=y+1
		y=1
		if data_isnumeric==len(current_lap):
			while y < len(current_lap):
				data_lap_list[0]=data_lap_list[0]+data_lap_list[y]
				print('data_lap_list[0] apres traitement isnumeric : ' + data_lap_list[0])
				y=y+1
				
			if int(data_lap_list[0])>=int(current_lap) and int(data_lap_list[0]) <= (int(current_lap)+2):
				print('we.... probably solved the problem')
				result_list_too_big = data_lap_list[0]
			else:
				result_list_too_big = 0

	return result_list_too_big