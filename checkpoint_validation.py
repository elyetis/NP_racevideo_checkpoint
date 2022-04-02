from cv2 import cv2
import pytesseract
import re

def checkpoint_basic_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, shift):
	temp=y_checkpoint
	
	if shift==1:
		y_checkpoint=y_checkpoint-vertical_shift_phone#I still need to make sure it work with multiple resolution, this is based on a single sample for 936p video
	
	sub_image = frame[y_checkpoint:y_checkpoint+h_checkpoint, x_checkpoint:x_checkpoint+w_checkpoint]
	gray = cv2.cvtColor(sub_image, cv2.COLOR_BGR2GRAY)
	gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
	
	
	data = pytesseract.image_to_string(gray, lang='eng', config='--psm 10').lower()
	data_checkpoint_list=re.findall(r'\d+', data)
	
	y_checkpoint=temp
	
	print('checkpoint_basic_processing : ')
	print(data)

	
	return data_checkpoint_list


	
def checkpoint_alternative_image_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, shift):
	temp=y_checkpoint
	
	if shift==1:
		y_checkpoint=y_checkpoint-vertical_shift_phone#I still need to make sure it work with multiple resolution, this is based on a single sample for 936p video
	
	sub_image = frame[y_checkpoint:y_checkpoint+h_checkpoint, x_checkpoint:x_checkpoint+w_checkpoint]
	gray = cv2.cvtColor(sub_image, cv2.IMREAD_GRAYSCALE)
	gray[gray < 240] = 0
	
	scaled = cv2.resize(gray, (0,0), fx=10, fy=10, interpolation = cv2.INTER_CUBIC)
	
	pre_processed = scaled

	data = pytesseract.image_to_string(pre_processed, lang='eng', config='--psm 6 --oem 3 tessedit_char_whitelist=0123456789').lower()
	data_checkpoint_list=re.findall(r'\d+', data)
	
	y_checkpoint=temp
	
	print('checkpoint_basic_processing : ')
	print(data)
	
	return data_checkpoint_list
	
	
	
def checkpoint_alternative_image_processing2(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, shift):
	temp=y_checkpoint
	
	if shift==1:
		y_checkpoint=y_checkpoint-vertical_shift_phone#I still need to make sure it work with multiple resolution, this is based on a single sample for 936p video
	
	sub_image = frame[y_checkpoint:y_checkpoint+h_checkpoint, x_checkpoint:x_checkpoint+w_checkpoint]
	gray = cv2.cvtColor(sub_image, cv2.IMREAD_GRAYSCALE)

	scaled = cv2.resize(gray, (0,0), fx=4, fy=4, interpolation = cv2.INTER_LINEAR)
	
	scaled[scaled < 230] = 0
	
	pre_processed = scaled

	data = pytesseract.image_to_string(pre_processed, lang='eng', config='--psm 10').lower()
	data_checkpoint_list=re.findall(r'\d+', data)
	
	y_checkpoint=temp
	
	print('checkpoint_basic_processing 2 : ')
	print(data)
	
	return data_checkpoint_list


	
def checkpoint_list_too_big(data_checkpoint_list, current_checkpoint, result_list_too_big):
	if len(data_checkpoint_list)>2:
		y=0
		data_isnumeric=0
		while y < len(current_checkpoint):
			if data_checkpoint_list[y].isnumeric :
				print('data_checkpoint_list isnumeric')
				data_isnumeric=data_isnumeric+1
			y=y+1
		y=1
		if data_isnumeric==len(current_checkpoint):
			while y < len(current_checkpoint):
				data_checkpoint_list[0]=data_checkpoint_list[0]+data_checkpoint_list[y]
				print('data_checkpoint_list[0] apres traitement isnumeric : ' + data_checkpoint_list[0])
				y=y+1
				
			if int(data_checkpoint_list[0])>=int(current_checkpoint) and int(data_checkpoint_list[0]) <= (int(current_checkpoint)+2):
				print('we.... probably solved the problem')
				result_list_too_big = data_checkpoint_list[0]
			else:
				result_list_too_big = 0

	return result_list_too_big