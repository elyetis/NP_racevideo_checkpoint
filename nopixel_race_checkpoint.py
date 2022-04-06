from cv2 import cv2
import pytesseract
#pytesseract.pytesseract.tesseract_cmd = 'F:\\Anaconda\\envs\\env_tesseract\\Library\\bin\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR\\tesseract.exe'
import re
from bounding_box import *
from checkpoint_validation import *
from lap_validation import *


print('OpenCV version: ' + cv2.__version__)

DICT = ['checkpoint']


print("Please input the number of lap ( 0 for a sprint ) : ")
number_of_lap = int(input(''))
#print("please input the final Total Time ( format is 00:00.000 )")#!!! I should be able to automate that part by checking when "Checkpoint" disapear from the UI
print('Please input the number of checkpoint as displayed by the UI ( finish line does not count ) : ')
final_checkpoint=input('')
print('Please input video file name ( with extension ) : ')
path = input('')#!!! should add a default value if empty, like race.mp4
print("Please input the final lap 'Current lap' time ( format is 00:00.000 ) : ")
final_laptime = input('')#!!! should be able to automate that part by checking the disapearance of the text checkpoint in the UI or 'Pos' y coordinate getting lower



vidcap = cv2.VideoCapture(path)

framenbr = 0
video_time=0
skip_duration_base_value=4000
skipping_frames=1
frame = vidcap.set(cv2.CAP_PROP_POS_MSEC, video_time)
success,frame = vidcap.read()

pytesseract_time_previous_checkpoint=0


result_list_too_big=str(0)

consecutive_skips=0#used so I know if i do consecutive skip forward or backward

current_lap=str(1)
current_checkpoint=str(1)
new_checkpoint=str(1)


current_time=0
minutes=0
secondes=0
milisec=0




print('Working...')


file = open('result.csv', 'w')


#We want the video lenght so we don't try to skip past it
fps=vidcap.get(cv2.CAP_PROP_FPS)
print(fps)
video_total_frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
print(video_total_frame_count)
video_total_duration = video_total_frame_count/fps
print(video_total_duration)
video_total_duration_miliseconds = video_total_duration*1000
print(video_total_duration_miliseconds)


# ----------------------------- Selecting the box where we use pytesseract to go our data-----------------------------------

#we go at the middle of the video to make sure the video started

video_time=video_total_duration_miliseconds/2

frame = vidcap.set(cv2.CAP_PROP_POS_MSEC, video_time)
success,frame = vidcap.read()


#but since we want the proper position of the race interface is, we make sure people doing it on a frame where the UI isn't moved by a phone notification
video_height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#print('video_height = ' + str(video_height))
vertical_shift_phone=round(int(video_height)/(9.61))#98 for 936p    -  112 for 1080p
 
#print('arondi calcul = ' + str(testestest))



answer='y'
print('Close the picture and press Enter if the race UI is where it should be ( no phone notification pushing it up ), otherwise input n')
cv2.imshow("frame", frame)
cv2.waitKey(0)
answer=input('')
while str(answer)=='n':
	video_time=video_time+4000
	frame = vidcap.set(cv2.CAP_PROP_POS_MSEC, video_time)
	success,frame = vidcap.read()
	
	cv2.imshow("frame", frame)
	cv2.waitKey(0)
	
	print('Again, close the picture and press Enter if the race UI is where it should be ( no phone notification pushing it up ), otherwise input n')
	answer=input('')

	
	
boundingbox_widget = BoundingBoxWidget(frame)
while True:
	print('With your mouse left button, select the whole race interface from top left to bottom right then press Enter')
	cv2.imshow('image', boundingbox_widget.show_image())
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	break


	
# ----------------------------- End of Selecting the box where we use pytesseract to go our data-----------------------------------


# ------------------------------------ Initialisation, looking for x/y/w/h pos of checkpoint, lap, current time etc------------------------------------------
sub_image = frame[boundingbox_widget.image_coordinates[0][1]:boundingbox_widget.image_coordinates[0][1]+(boundingbox_widget.image_coordinates[1][1] - boundingbox_widget.image_coordinates[0][1]), boundingbox_widget.image_coordinates[0][0]:boundingbox_widget.image_coordinates[0][0]+(boundingbox_widget.image_coordinates[1][0] - boundingbox_widget.image_coordinates[0][0])]
gray = cv2.cvtColor(sub_image, cv2.COLOR_BGR2GRAY)
gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR) #don't know if the resize actually improve detection
data = pytesseract.image_to_string(gray, lang='eng', config='--psm 10').lower()




data = pytesseract.image_to_data(gray, output_type='dict')
keys = list(data.keys())

detection_score=0
n_boxes = len(data['text'])
#can be made better by putting it in a while detection_score<3, with a time skip each time it isn't able to find all the necessary lignes
while detection_score<3:
	for i in range(n_boxes):
		print(data['text'][i])
		if int(data['conf'][i])>60:
			if data['text'][i]=='Checkpoint':

				detection_score=detection_score+1
				
				y_checkpoint=round((data['top'][i]/2)+boundingbox_widget.image_coordinates[0][1]-1)#-1 = margin
				x_checkpoint=round((data['left'][i]/2)+boundingbox_widget.image_coordinates[0][0]-1)
				h_checkpoint=round((data['height'][i]/2)+1)
				#!!! need to check that i+1 formating is xx/xx otherwise we need to go on another frame 
				w_checkpoint=round((data['width'][i]+(data['width'][i]*0.87))/2)
				#frame = cv2.rectangle(frame, (x_checkpoint, y_checkpoint), (x_checkpoint + w_checkpoint, y_checkpoint + h_checkpoint), (0, 255, 0), 1)
				
				x_time=round((data['left'][i]+data['width'][i])/2+boundingbox_widget.image_coordinates[0][0]+4)#+10 = margin
				
				w_time=round(w_checkpoint-data['width'][i]/2)-4# same margin as x_time
				
				if number_of_lap > 1 and data['text'][i-3]=='Lap': #a 1 lap circuit is a sprint
					detection_score=detection_score+1
					
					y_lap=round((data['top'][i-3]/2)+boundingbox_widget.image_coordinates[0][1]-2)
					x_lap=x_time+15 #!!! valeur fix a modifier pour que cela scale avec la resolution de l'ui
					h_lap=round((data['height'][i-3]/2))
					w_lap=w_time-14 #!!! valeur fix a modifier pour que cela scale avec la resolution de l'ui
				
				
			if data['text'][i]=='Current':
				detection_score=detection_score+1
				
				y_time=round((data['top'][i])/2+boundingbox_widget.image_coordinates[0][1]-1)#-1 = margin
				h_time=round((data['height'][i])/2+1)
				
				
				
				#frame = cv2.rectangle(frame, (x_time, y_time), (x_time + w_time, y_time + h_time), (0, 255, 0), 1)
			if data['text'][i]=='Total' and number_of_lap < 2:
				detection_score=detection_score+1

			
	if detection_score==3:
		break
		
	print('detection score = ' + str(detection_score))	

	
	#cv2.imshow("gray", gray)
	#cv2.waitKey(0)

	video_time=video_time + 500
	frame = vidcap.set(cv2.CAP_PROP_POS_MSEC, video_time)
	success,frame = vidcap.read()				
	
	sub_image = frame[boundingbox_widget.image_coordinates[0][1]:boundingbox_widget.image_coordinates[0][1]+(boundingbox_widget.image_coordinates[1][1] - boundingbox_widget.image_coordinates[0][1]), boundingbox_widget.image_coordinates[0][0]:boundingbox_widget.image_coordinates[0][0]+(boundingbox_widget.image_coordinates[1][0] - boundingbox_widget.image_coordinates[0][0])]
	gray = cv2.cvtColor(sub_image, cv2.COLOR_BGR2GRAY)
	gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR) #don't know if the resize actually improve detection
	data = pytesseract.image_to_string(gray, lang='eng', config='--psm 10').lower()
	

	data = pytesseract.image_to_data(gray, output_type='dict')
	keys = list(data.keys())

	detection_score=0
	n_boxes = len(data['text'])
# ------------------------------------ Initialisation, looking for x/y/w/h pos of checkpoint, lap, current time etc------------------------------------------	


	
# reset to the start of the video
video_time=0
frame = vidcap.set(cv2.CAP_PROP_POS_MSEC, video_time)
success,frame = vidcap.read()


print('y_checkpoint : ' + str(y_checkpoint) + 'x_checkpoint : ' + str(x_checkpoint) + 'h_checkpoint : ' + str(h_checkpoint) + 'w_checkpoint : ' + str(w_checkpoint))



# ---------------------------------------- We look for the start of the race---------------------------------------------

sub_image = frame[y_checkpoint:y_checkpoint+h_checkpoint, x_checkpoint:x_checkpoint+w_checkpoint]
gray = cv2.cvtColor(sub_image, cv2.COLOR_BGR2GRAY)
gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
data = pytesseract.image_to_string(gray, lang='eng', config='--psm 10').lower()



#to achieve that we try to find when "checkpoint" appear on the screen 
#!!! could also use alternative check for Lap, Current etc. for better accuracy

skip_duration = skip_duration_base_value
video_time=skip_duration

course_started=0

#first we skip frames to quickly find around where it start
while skipping_frames==1:
	frame = vidcap.set(cv2.CAP_PROP_POS_MSEC, video_time)
	success,frame = vidcap.read()

	print('\n -------------skiping frame------------- ')
	print('video_time: ' + str(video_time))
	sub_image = frame[y_checkpoint:y_checkpoint+h_checkpoint, x_checkpoint:x_checkpoint+w_checkpoint]
	gray = cv2.cvtColor(sub_image, cv2.COLOR_BGR2GRAY)
	gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
	data = pytesseract.image_to_string(gray, lang='eng', config='--psm 10').lower()
	
	print('data: ' + data)

	if any(word in data for word in DICT):
		print('any(word in data for word in DICT)')
		course_started=1
	else:
		print('else : any(word in data for word in DICT)')
		course_started=0
	
	if skip_duration<150 and consecutive_skips>0:#150 peut etre changé pour une valeur plus faible ?
		print('skip_duration<150')
		video_time=video_time-skip_duration
		frame = vidcap.set(cv2.CAP_PROP_POS_MSEC, video_time)
		skipping_frames=0
		break
		
	#now we go frame by frame to find the exact starting time
	if course_started==1:
		print('if course_started==1')
		print('consecutive_skips' + str(consecutive_skips))
		
		
		if consecutive_skips > 0:
			consecutive_skips=-1
			skip_duration=skip_duration/2
		else:
			consecutive_skips=consecutive_skips-1
			if consecutive_skips>-3:
				skip_duration=skip_duration/2
				
		video_time=video_time-skip_duration
	else:
		print('else')
		print('consecutive_skips' + str(consecutive_skips))
		
		
		if consecutive_skips < 0:
			consecutive_skips=1
			skip_duration=skip_duration/2
		else:
			consecutive_skips=consecutive_skips+1
			if consecutive_skips<3:
				skip_duration=skip_duration/2
			
		video_time=video_time+skip_duration
	

while skipping_frames==0:
	framenbr += 1
	success,frame = vidcap.read()

	print('Frame number: ' + str(framenbr))
	sub_image = frame[y_checkpoint:y_checkpoint+h_checkpoint, x_checkpoint:x_checkpoint+w_checkpoint]
	gray = cv2.cvtColor(sub_image, cv2.COLOR_BGR2GRAY)
	gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
	data = pytesseract.image_to_string(gray, lang='eng', config='--psm 10').lower()
	
	
	
	if any(word in data for word in DICT):
		print('any(word in data for word in DICT)')
		video_time_start_race=vidcap.get(cv2.CAP_PROP_POS_MSEC)
		video_time_previous_checkpoint=video_time_start_race
		calculated_time_previous_checkpoint=0
		print('video_time_start_race = ' + str(video_time_start_race))
		
		skipping_frames=1
		break
#------------------------------------------------------------------------------------------------------------------------------		

#we get the video time of when the race start
video_time = vidcap.get(cv2.CAP_PROP_POS_MSEC)	
	
print('Success, race starting at frame : ' + str(framenbr))


skip_duration = skip_duration_base_value
video_time=video_time+skip_duration
consecutive_skips=0

print('\nbefore while video_time : ' + str(video_time))



print('\n current_checkpoint : ' + current_checkpoint + ' new_checkpoint : ' + new_checkpoint)
print('\n video_time : ' + str(video_time) + ' skip_duration : ' + str(skip_duration))

current_lap = 1

while success :
	print('while success')
	
	#_______________________ SKIPING FRAME ___CHECKPOINT _______________________
	while skipping_frames==1:
	
		
		data_checkpoint_list_validation = 0
		while data_checkpoint_list_validation == 0: 
		
			print('---------------SKIPING FRAME---------------')
			print('data_checkpoint_list_validation == 0')
			print('video_time == ' + str(video_time))
			
			frame = vidcap.set(cv2.CAP_PROP_POS_MSEC, video_time)
			success,frame = vidcap.read()
		
			#basic pytesseract processing
			data_checkpoint_list=checkpoint_basic_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 0)
			if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=(int(current_checkpoint)-1) and int(data_checkpoint_list[0]) <= (int(current_checkpoint)+4):
				new_checkpoint=str(data_checkpoint_list[0])#could simplifu it by putting it after the while**
				print('len(data_checkpoint_list) = ' + str(len(data_checkpoint_list)))
				print('data_checkpoint_list[0] = ' + str(data_checkpoint_list[0]))
				break
				
				
			#basic pytesseract processing in case of phone notification, so shift = 1
			data_checkpoint_list=checkpoint_basic_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 1)
			if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=(int(current_checkpoint)-1) and int(data_checkpoint_list[0]) <= (int(current_checkpoint)+4):
				new_checkpoint=str(data_checkpoint_list[0])
				print('len(data_checkpoint_list) = ' + str(len(data_checkpoint_list)))
				print('data_checkpoint_list[0] = ' + str(data_checkpoint_list[0]))
				break
				
			# ajouter checkpoint_list_too_big meme en l'absence d'un mage processing important ?
				
			
			#alternative image processing
			data_checkpoint_list=checkpoint_alternative_image_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 0)
			if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=(int(current_checkpoint)-1) and int(data_checkpoint_list[0]) <= (int(current_checkpoint)+4):
				new_checkpoint=str(data_checkpoint_list[0])
				print('len(data_checkpoint_list) = ' + str(len(data_checkpoint_list)))
				print('data_checkpoint_list[0] = ' + str(data_checkpoint_list[0]))
				break
			
			#kind of a brut force solution to a problem where simething like "17/40" would be read 1/7/40
			result_list_too_big=checkpoint_list_too_big(data_checkpoint_list, current_checkpoint, result_list_too_big)
			if int(result_list_too_big)>=(int(current_checkpoint)-1) and int(result_list_too_big) <= (int(current_checkpoint)+4):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
				new_checkpoint=str(result_list_too_big)
				print('result = ' + str(result_list_too_big))
				break
				
			#alternative image processing  in case of phone notification, so shift = 1
			data_checkpoint_list=checkpoint_alternative_image_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 1)
			if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=(int(current_checkpoint)-1) and int(data_checkpoint_list[0]) <= (int(current_checkpoint)+4):
				new_checkpoint=str(data_checkpoint_list[0])
				print('len(data_checkpoint_list) = ' + str(len(data_checkpoint_list)))
				print('data_checkpoint_list[0] = ' + str(data_checkpoint_list[0]))
				break
			
			
			#kind of a brut force solution to a problem where simething like "17/40" would be read 1/7/40, on the previous result with phone notification up
			result_list_too_big=checkpoint_list_too_big(data_checkpoint_list, current_checkpoint, result_list_too_big)
			if int(result_list_too_big)>=(int(current_checkpoint)-1) and int(result_list_too_big) <= (int(current_checkpoint)+4):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
				new_checkpoint=str(result_list_too_big)
				print('result = ' + str(result_list_too_big))
				break
				
				
			#another image processing - might need to disable not much testing on this one
			data_checkpoint_list=checkpoint_alternative_image_processing2(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 0)
			if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=(int(current_checkpoint)-1) and int(data_checkpoint_list[0]) <= (int(current_checkpoint)+4):
				new_checkpoint=str(data_checkpoint_list[0])
				print('len(data_checkpoint_list) = ' + str(len(data_checkpoint_list)))
				print('data_checkpoint_list[0] = ' + str(data_checkpoint_list[0]))
				break
			
			
			result_list_too_big=checkpoint_list_too_big(data_checkpoint_list, current_checkpoint, result_list_too_big)
			if int(result_list_too_big)>=(int(current_checkpoint)-1) and int(result_list_too_big) <= (int(current_checkpoint)+4):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
				new_checkpoint=str(result_list_too_big)
				print('result = ' + str(result_list_too_big))
				break
				

			data_checkpoint_list=checkpoint_alternative_image_processing2(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 1)
			if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=(int(current_checkpoint)-1) and int(data_checkpoint_list[0]) <= (int(current_checkpoint)+4):
				new_checkpoint=str(data_checkpoint_list[0])
				print('len(data_checkpoint_list) = ' + str(len(data_checkpoint_list)))
				print('data_checkpoint_list[0] = ' + str(data_checkpoint_list[0]))
				break
			
			
			result_list_too_big=checkpoint_list_too_big(data_checkpoint_list, current_checkpoint, result_list_too_big)
			if int(result_list_too_big)>=(int(current_checkpoint)-1) and int(result_list_too_big) <= (int(current_checkpoint)+4):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
				new_checkpoint=str(result_list_too_big)#possiblement à placer apres la while
				print('result = ' + str(result_list_too_big))
				break
				

			
			#if nothing worked we slightly go backward or forward
			if consecutive_skips>=0:
				video_time=video_time+15
			else:
				video_time=video_time-15
			print('going on the next frame since nothing worked')

			
			
		print('\n current_checkpoint : ' + str(current_checkpoint) + ' new_checkpoint : ' + str(new_checkpoint) + ' skip_duration = ' + str(skip_duration))
		
		
		if skip_duration<150:#would need more testing to see what value give the best performance
			print('skip_duration<150')
			if str(current_checkpoint)==str(new_checkpoint):
				skipping_frames=0
				break
				#we stop skipping frames and go for frame by frame
		
		if str(current_checkpoint)!=str(new_checkpoint):
			print('if current_checkpoint!=new_checkpoint')
			print('consecutive_skips' + str(consecutive_skips))
			
			#skip backward
			if consecutive_skips > 0:
				consecutive_skips=-1
				skip_duration=skip_duration/2
			else:
				consecutive_skips=consecutive_skips-1
				#if consecutive_skips>-3:
					#skip_duration=skip_duration/2
					
			video_time=video_time-skip_duration
		else:
			print('else')
			print('consecutive_skips' + str(consecutive_skips))
			
			#skip forward
			if consecutive_skips < 0:
				consecutive_skips=1
				skip_duration=skip_duration/2
			else:
				consecutive_skips=consecutive_skips+1

				
			video_time=video_time+skip_duration
	#-------------------------------------------------------------------------------------------------------------------------
	
	print('-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-')
	print('going frame by frame')
	consecutive_skips=0

		
	#_______________________ FRAME by FRAME ___CHECKPOINT _______________________
	while skipping_frames==0:
		
		print('while skipping_frames == 0')
		
		
		
		data_checkpoint_list_validation = 0
		while data_checkpoint_list_validation == 0: 
		
			print('---------------FRAME BY FRAME---------------')
			print('data_checkpoint_list_validation == 0')
			print('video_time == ' + str(video_time))
			
			success,frame = vidcap.read()
		
			#basic process
			data_checkpoint_list=checkpoint_basic_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 0)
			if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=(int(current_checkpoint)-1) and int(data_checkpoint_list[0]) <= (int(current_checkpoint)+1):
				new_checkpoint=str(data_checkpoint_list[0])
				print('len(data_checkpoint_list) = ' + str(len(data_checkpoint_list)))
				print('data_checkpoint_list[0] = ' + str(data_checkpoint_list[0]))
				break
				
				
			#notification phone up, so shift = 1 
			data_checkpoint_list=checkpoint_basic_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 1)
			if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=(int(current_checkpoint)-1) and int(data_checkpoint_list[0]) <= (int(current_checkpoint)+1):
				new_checkpoint=str(data_checkpoint_list[0])
				print('len(data_checkpoint_list) = ' + str(len(data_checkpoint_list)))
				print('data_checkpoint_list[0] = ' + str(data_checkpoint_list[0]))
				break
				
			
			#alternative image processing
			data_checkpoint_list=checkpoint_alternative_image_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 0)
			if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=(int(current_checkpoint)-1) and int(data_checkpoint_list[0]) <= (int(current_checkpoint)+1):
				new_checkpoint=str(data_checkpoint_list[0])
				print('len(data_checkpoint_list) = ' + str(len(data_checkpoint_list)))
				print('data_checkpoint_list[0] = ' + str(data_checkpoint_list[0]))
				break
			
			
			result_list_too_big=checkpoint_list_too_big(data_checkpoint_list, current_checkpoint, result_list_too_big)
			if int(result_list_too_big)>=(int(current_checkpoint)-1) and int(result_list_too_big) <= (int(current_checkpoint)+2):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
				new_checkpoint=str(result_list_too_big)
				print('result = ' + str(result_list_too_big))
				break
				
			#phone up, shift = 1 en argument
			data_checkpoint_list=checkpoint_alternative_image_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 1)
			if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=(int(current_checkpoint)-1) and int(data_checkpoint_list[0]) <= (int(current_checkpoint)+1):
				new_checkpoint=str(data_checkpoint_list[0])
				print('len(data_checkpoint_list) = ' + str(len(data_checkpoint_list)))
				print('data_checkpoint_list[0] = ' + str(data_checkpoint_list[0]))
				break
			
			
			result_list_too_big=checkpoint_list_too_big(data_checkpoint_list, current_checkpoint, result_list_too_big)
			if int(result_list_too_big)>=(int(current_checkpoint)-1) and int(result_list_too_big) <= (int(current_checkpoint)+1):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
				new_checkpoint=str(result_list_too_big)
				print('result = ' + str(result_list_too_big))
				break
				
				
			print('going on the next frame since nothing worked')

			
		
		
		#_______________________ NEW CHECKPOINT FOUND ________________________
		if str(current_checkpoint)==str(int(new_checkpoint)-1):
			print('if current_checkpoint!=new_checkpoint')
			print('current_checkpoint = ' + str(current_checkpoint) + ' | final_checkpoint = ' + str(final_checkpoint))
		
			current_checkpoint=new_checkpoint
		
			#creating sub picture with the current laptime
			sub_image_time = frame[y_time:y_time+h_time, x_time:x_time+w_time]
			gray_time = cv2.cvtColor(sub_image_time, cv2.COLOR_BGR2GRAY)
			gray_time = cv2.resize(gray_time, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
			data_time = pytesseract.image_to_string(gray_time, lang='eng', config='--psm 10').lower()
			#int into list
			data_time_list=re.findall(r'\d+', data_time)
			print('\ndata_time : ' + data_time)
			
			#fallback calculation in case pysseract does not properly read the time
			video_time_new_checkpoint=vidcap.get(cv2.CAP_PROP_POS_MSEC)
			calculated_time_new_checkpoint=video_time_new_checkpoint-video_time_start_race
			calculated_sector_duration=round(calculated_time_new_checkpoint-calculated_time_previous_checkpoint)
			calculated_total_time=round(pytesseract_time_previous_checkpoint+calculated_sector_duration)
			
			print('------ info time newcheckpoint -------') 
			print('video_time_start_race : ' + str(video_time_start_race))
			print('vidcap.get(cv2.CAP_PROP_POS_MSEC) : ' + str(video_time_new_checkpoint))
			print('calculated_time_new_checkpoint : ' + str(calculated_time_new_checkpoint))
			print('calculated_sector_duration : ' + str(calculated_sector_duration)) 
			print('calculated_time_previous_checkpoint : ' + str(calculated_time_previous_checkpoint))
			print('pytesseract_time_previous_checkpoint : ' + str(pytesseract_time_previous_checkpoint))
			print('calculated_total_time : ' + str(calculated_total_time)) 			
			print('------ info time newcheckpoint -------') 
			
			
			#we make sure the data_time we got is actually of the right format, three series of numbers
			data_time_validation=1
			
			while data_time_validation == 1:
				if len(data_time_list)!=3:
					print('data_time_list too short')
					data_time_validation=0
					break
				if not data_time_list[0].isnumeric:
					print('data_time_list[0] isNOTnumeric')
					data_time_validation=0
					break
				if int(data_time_list[0])>60:
					print('data_time_list[0] > 60')
					data_time_validation=0
					break
				if not data_time_list[1].isnumeric:
					print('data_time_list[1] isNOTnumeric')
					data_time_validation=0
					break
				if int(data_time_list[1])>60:
					print('data_time_list[0] > 60')
					data_time_validation=0
					break
				if not data_time_list[2].isnumeric:
					print('data_time_list[2] isNOTnumeric')
					data_time_validation=0
					break
				if int(data_time_list[2])>999:
					print('data_time_list[2] > 999')
					data_time_validation=0
					break
				break
			
				

				
			if data_time_validation == 1:
				minutes=data_time_list[0]
				secondes=data_time_list[1]
				milisec=data_time_list[2]
				print('\n minutes : ' + minutes + ' secondes : ' + secondes + ' milisec : ' + milisec)
				pytesseract_time_previous_checkpoint = int(minutes)*60000+int(secondes)*1000+int(milisec)
				
				#we still check if there is not a discrepancy between the value read, and the value calculated, if it's too big we prefer to trust the calculated value
				if abs(int(pytesseract_time_previous_checkpoint)-int(calculated_total_time))>200: #we accept a 200ms discrepancy, can be modified
					print('writing calculated_total_time in file...')
					file.write(str(calculated_total_time)+'|')
					pytesseract_time_previous_checkpoint=calculated_total_time			
				else:
					print('writing pytesseract_time_previous_checkpoint in file...')
					file.write(str(pytesseract_time_previous_checkpoint)+'|')
			else:
				#data_time isn't usable so we fall back on the video time calculation
				
				print(pytesseract_time_previous_checkpoint)
				print(calculated_time_new_checkpoint)
				print(calculated_sector_duration)
				print(calculated_total_time)
				
				print('writing calculated_total_time in file...')
				file.write(str(calculated_total_time)+'|')				

				pytesseract_time_previous_checkpoint=calculated_total_time
			
			
			skipping_frames=1
			video_time=vidcap.get(cv2.CAP_PROP_POS_MSEC)
			print('video_time = ' + str(video_time))
			
			video_time_previous_checkpoint=video_time_new_checkpoint
			calculated_time_previous_checkpoint=calculated_time_new_checkpoint
			
			
			print('__________________________________________________________\n')
			
			#back to skipping frame but making sure we don't go past the video lenght
			skip_duration=skip_duration_base_value
			if (video_time+skip_duration)>video_total_duration_miliseconds:
				print('On depasserai la duree de la video avec ce frameskip')
				skip_duration=(video_total_duration_miliseconds-video_time)
		
	
	
	
	#exit the program if last checkpoint of last lap, possibility of improvement if we actually detect the finish line (!!!)
	if int(current_lap) == int(number_of_lap) or int(number_of_lap) == 0:
		if int(current_checkpoint) == int(final_checkpoint):
			temp = re.findall(r'\d+', final_laptime)
			temp2 = int(temp[0])*60000+int(temp[1])*1000+int(temp[2])
			file.write(str(temp2))
			print('Finished')
			break

	
	#_________________________________________________________________________________________________________________________________________________
	#________________________________________________________________ LAP ____________________________________________________________________________
	#_________________________________________________________________________________________________________________________________________________
	
	if current_checkpoint==final_checkpoint:
		
		#_______________________ LAP SKIPING FRAME ________________________
			
		while skipping_frames==1:

		
			data_lap_list_validation = 0
			while data_lap_list_validation == 0:
			
				print('---------------SKIPING FRAME---------------')
				print('data_lap_list_validation == 0')
				print('video_time == ' + str(video_time))
				
				frame = vidcap.set(cv2.CAP_PROP_POS_MSEC, video_time)
				success,frame = vidcap.read()
			
				#base process
				data_lap_list=lap_basic_processing(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, 0)
				if len(data_lap_list)==2 and int(data_lap_list[0])>=(int(current_lap)-1) and int(data_lap_list[0]) <= (int(current_lap)+1):
					new_lap=str(data_lap_list[0])
					print('len(data_lap_list) = ' + str(len(data_lap_list)))
					print('data_lap_list[0] = ' + str(data_lap_list[0]))
					break
					
					
				#phone up, shift = 1 
				data_lap_list=lap_basic_processing(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, 1)
				if len(data_lap_list)==2 and int(data_lap_list[0])>=(int(current_lap)-1) and int(data_lap_list[0]) <= (int(current_lap)+1):
					new_lap=str(data_lap_list[0])
					print('len(data_lap_list) = ' + str(len(data_lap_list)))
					print('data_lap_list[0] = ' + str(data_lap_list[0]))
					break
					

					
				#----------------------------we also have the option of checking the checkpoint number, new lap if checkpoint goes back to 1	
				#base
				data_checkpoint_list=checkpoint_basic_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 0)
				if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=1 and int(data_checkpoint_list[0])<=3:
					new_lap=str(int(current_lap)+1)
					print('new_lap = ' + str(new_lap))
					print('NEXT LAP BASED ON CHECKPOINT CHECK')
					break
				else:
					if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])==int(final_checkpoint):
						new_lap=str(current_lap)
						print('new_lap = ' + str(new_lap))
						print('STILL PREVIOUS LAP BASED ON CHECKPOINT CHECK')
						break
					
					
				#phone up, shift = 1
				data_checkpoint_list=checkpoint_basic_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 1)
				if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])>=1 and int(data_checkpoint_list[0])<=3:
					new_lap=str(int(current_lap)+1)
					print('new_lap = ' + str(new_lap))
					print('NEXT LAP BASED ON CHECKPOINT CHECK')
					break
				else:
					if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])==int(final_checkpoint):
						new_lap=current_lap
						print('new_lap = ' + str(new_lap))
						print('STILL PREVIOUS LAP BASED ON CHECKPOINT CHECK')
						break
				
					
				#----------------------------another image processing	
				
				data_lap_list=lap_alternative_image_processing(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, 0)
				if len(data_lap_list)==2 and int(data_lap_list[0])>=(int(current_lap)-1) and int(data_lap_list[0]) <= (int(current_lap)+1):
					new_lap=str(data_lap_list[0])
					print('len(data_lap_list) = ' + str(len(data_lap_list)))
					print('data_lap_list[0] = ' + str(data_lap_list[0]))
					break
				
				
				result_list_too_big=lap_list_too_big(data_lap_list, current_lap, result_list_too_big)
				if int(result_list_too_big)>=(int(current_lap)-1) and int(result_list_too_big) <= (int(current_lap)+1):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
					new_lap=str(result_list_too_big)
					print('result = ' + str(result_list_too_big))
					break
					
				#phone up, shift = 1
				data_lap_list=lap_alternative_image_processing(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, 1)
				if len(data_lap_list)==2 and int(data_lap_list[0])>=(int(current_lap)-1) and int(data_lap_list[0]) <= (int(current_lap)+1):
					new_lap=str(data_lap_list[0])
					print('len(data_lap_list) = ' + str(len(data_lap_list)))
					print('data_lap_list[0] = ' + str(data_lap_list[0]))
					break
				
				
				result_list_too_big=lap_list_too_big(data_lap_list, current_lap, result_list_too_big)
				if int(result_list_too_big)>=(int(current_lap)-1) and int(result_list_too_big) <= (int(current_lap)+1):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
					new_lap=str(result_list_too_big)
					print('result = ' + str(result_list_too_big))
					break
					
					
				#----------------------------another image processing - !!! might need to disable not much testing on this one
				
				data_lap_list=lap_alternative_image_processing2(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, 0)
				if len(data_lap_list)==2 and int(data_lap_list[0])>=(int(current_lap)-1) and int(data_lap_list[0]) <= (int(current_lap)+1):
					new_lap=str(data_lap_list[0])
					print('len(data_lap_list) = ' + str(len(data_lap_list)))
					print('data_lap_list[0] = ' + str(data_lap_list[0]))
					break
				
				
				result_list_too_big=lap_list_too_big(data_lap_list, current_lap, result_list_too_big)
				if int(result_list_too_big)>=(int(current_lap)-1) and int(result_list_too_big) <= (int(current_lap)+1):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
					new_lap=str(result_list_too_big)
					print('result = ' + str(result_list_too_big))
					break
					
				#phone up, shift = 1
				data_lap_list=lap_alternative_image_processing2(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, 1)
				if len(data_lap_list)==2 and int(data_lap_list[0])>=(int(current_lap)-1) and int(data_lap_list[0]) <= (int(current_lap)+1):
					new_lap=str(data_lap_list[0])
					print('len(data_lap_list) = ' + str(len(data_lap_list)))
					print('data_lap_list[0] = ' + str(data_lap_list[0]))
					break
				
				
				result_list_too_big=lap_list_too_big(data_lap_list, current_lap, result_list_too_big)
				if int(result_list_too_big)>=(int(current_lap)-1) and int(result_list_too_big) <= (int(current_lap)+1):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
					new_lap=str(result_list_too_big)
					print('result = ' + str(result_list_too_big))
					break
					

				
				#nothing worked skipping a frame
				if consecutive_skips>=0:
					video_time=video_time+15
				else:
					video_time=video_time-15
				print('going on the next frame since nothing worked')

				
			print('\n current_lap : ' + str(current_lap) + ' new_lap : ' + str(new_lap) + ' skip_duration = ' + str(skip_duration))
			
			
			if int(skip_duration)<150:# can be modified for better optimisation ?
				print('skip_duration<150')	
				if int(current_lap)==int(new_lap):
					skipping_frames=int(0)
					print('skipping_frames = ' + str(skipping_frames))
					break
					#stop skipping frame, going frame by frame now
			
			if int(current_lap)!=int(new_lap):
				print('if current_lap!=new_lap')
				print('consecutive_skips = ' + str(consecutive_skips))
				
				#skip backward
				if consecutive_skips > 0:
					print('on a skip jusqu au lap suivant, on va donc skip backward')
					consecutive_skips=-1
					skip_duration=skip_duration/2
				else:
					consecutive_skips=consecutive_skips-1
					print('on continue de skip backward puisque toujours au meme lap')

						
				video_time=video_time-skip_duration
			else:
				print('else, on skip forward')
				print('consecutive_skips = ' + str(consecutive_skips))
				
				#skip forward
				if consecutive_skips < 0:
					consecutive_skips=1
					skip_duration=skip_duration/2
				else:
					consecutive_skips=consecutive_skips+1

					
				video_time=video_time+skip_duration

		#-------------------------------------------------------------------------------------------------------------------------
		

		
		#_______________________ LAP FRAME BY FRAME _______________________
		while skipping_frames==0:
			print('while skipping_frames == 0')
			
			
			data_lap_list_validation = 0
			while data_lap_list_validation == 0:
			
				print('---------------FRAME BY FRAME---------------')
				print('data_lap_list_validation == 0')
				print('video_time == ' + str(video_time))
				
				success,frame = vidcap.read()
			
				#base
				data_lap_list=lap_basic_processing(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, 0)
				if len(data_lap_list)==2 and int(data_lap_list[0])>=(int(current_lap)-1) and int(data_lap_list[0]) <= (int(current_lap)+1):#!!passer -1 a -0?
					new_lap=str(data_lap_list[0])
					print('len(data_lap_list) = ' + str(len(data_lap_list)))
					print('data_lap_list[0] = ' + str(data_lap_list[0]))
					break
					
					
				#phone up, shift = 1
				data_lap_list=lap_basic_processing(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, 1)
				if len(data_lap_list)==2 and int(data_lap_list[0])>=(int(current_lap)-1) and int(data_lap_list[0]) <= (int(current_lap)+1):
					new_lap=str(data_lap_list[0])
					print('len(data_lap_list) = ' + str(len(data_lap_list)))
					print('data_lap_list[0] = ' + str(data_lap_list[0]))
					break
					
					
				#----------------------------we also have the option of checking the checkpoint number, new lap if checkpoint goes back to 1	
				data_checkpoint_list=checkpoint_basic_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 0)
				if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])==1:
					new_lap=str(int(current_lap)+1)
					print('new_lap = ' + str(new_lap))
					print('NEXT LAP BASED ON CHECKPOINT CHECK FRAME BY FRAME')
					break
				else:
					if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])==int(final_checkpoint):
						new_lap=current_lap
						print('new_lap = ' + str(new_lap))
						print('STILL PREVIOUS LAP BASED ON CHECKPOINT CHECK')
						break
					
					
				#phone up, shift = 1
				data_checkpoint_list=checkpoint_basic_processing(y_checkpoint, x_checkpoint, h_checkpoint, w_checkpoint, frame, vertical_shift_phone, 1)
				if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])==1:
					new_lap=str(int(current_lap)+1)
					print('new_lap = ' + str(new_lap))
					print('NEXT LAP BASED ON CHECKPOINT CHECK')
					break
				else:
					if len(data_checkpoint_list)==2 and int(data_checkpoint_list[0])==int(final_checkpoint):
						new_lap=current_lap
						print('new_lap = ' + str(new_lap))
						print('STILL PREVIOUS LAP BASED ON CHECKPOINT CHECK')
						break

				
				#alternative image processing
				data_lap_list=lap_alternative_image_processing(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, 0)
				if len(data_lap_list)==2 and int(data_lap_list[0])>=(int(current_lap)-1) and int(data_lap_list[0]) <= (int(current_lap)+1):
					new_lap=str(data_lap_list[0])
					print('len(data_lap_list) = ' + str(len(data_lap_list)))
					print('data_lap_list[0] = ' + str(data_lap_list[0]))
					break
				
				
				result_list_too_big=lap_list_too_big(data_lap_list, current_lap, result_list_too_big)
				if int(result_list_too_big)>=(int(current_lap)-1) and int(result_list_too_big) <= (int(current_lap)+2):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
					new_lap=str(result_list_too_big)
					print('result = ' + str(result_list_too_big))
					break
					
				#phone up, shift = 1 
				data_lap_list=lap_alternative_image_processing(y_lap, x_lap, h_lap, w_lap, frame, vertical_shift_phone, 1)
				if len(data_lap_list)==2 and int(data_lap_list[0])>=(int(current_lap)-1) and int(data_lap_list[0]) <= (int(current_lap)+1):
					new_lap=str(data_lap_list[0])
					print('len(data_lap_list) = ' + str(len(data_lap_list)))
					print('data_lap_list[0] = ' + str(data_lap_list[0]))
					break
				
				
				result_list_too_big=lap_list_too_big(data_lap_list, current_lap, result_list_too_big)
				if int(result_list_too_big)>=(int(current_lap)-1) and int(result_list_too_big) <= (int(current_lap)+1):#on pourrai ajouter un check qui s'assure que la valeur trouvé est realiste
					new_lap=str(result_list_too_big)
					print('result = ' + str(result_list_too_big))
					break
					
					
	
				print('going on the next frame since nothing worked')
				
			print('new_lap = ' + str(new_lap) + ' | current lap = ' + str(current_lap))	
			
			if int(new_lap)==int(current_lap)+1:
				
				
				#fallback calculation in case pysseract does not properly read the time
				video_time_new_checkpoint=vidcap.get(cv2.CAP_PROP_POS_MSEC)
				calculated_time_new_checkpoint=video_time_new_checkpoint-video_time_start_race
				calculated_sector_duration=round(calculated_time_new_checkpoint-calculated_time_previous_checkpoint)
				calculated_total_time=round(pytesseract_time_previous_checkpoint+calculated_sector_duration)
				
				print('------ info time newcheckpoint -------') 
				print('video_time_start_race : ' + str(video_time_start_race)) 
				print('affichage de vidcap.get(cv2.CAP_PROP_POS_MSEC) : ' + str(video_time_new_checkpoint)) 
				print('calculated_time_new_checkpoint : ' + str(calculated_time_new_checkpoint))
				print('calculated_sector_duration : ' + str(calculated_sector_duration)) 
				print('calculated_time_previous_checkpoint : ' + str(calculated_time_previous_checkpoint))
				print('calculated_total_time : ' + str(calculated_total_time)) 			
				print('------ info time newcheckpoint -------') 
					
				
				
				file.write(str(calculated_total_time) + '\n')
				
				print('______________________________----- INITIALISATION NEW LAP -----______________________________')
				
				skipping_frames=1
				current_lap=int(current_lap)+1
				current_checkpoint=1
				new_checkpoint=1
				current_time=0
				minutes=0
				secondes=0
				milisec=0
				result_list_too_big=str(0)
				consecutive_skips=0
				pytesseract_time_previous_checkpoint=0
				
				skipping_frames=1
				skip_duration=skip_duration_base_value

				video_time=vidcap.get(cv2.CAP_PROP_POS_MSEC)
				print('video_time = ' + str(video_time))
				
				video_time_previous_checkpoint=video_time_new_checkpoint
				calculated_time_previous_checkpoint=calculated_time_new_checkpoint
					
			

cv2.waitKey(0)
		
