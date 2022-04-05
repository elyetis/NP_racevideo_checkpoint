This program allow you to get sector time from the video of a race by analysing it with Pysseract.

Ideal scenario would be someone making something like a shared google sheet with different race PB / LR etc.


## Note :
- only really tested on 936p/1080p video, it should also work on 720p video but I don't know if the lower resolution still make it readable enough for tysseract, probably depend on the scale of the UI
- don't expect ultra high accuracy, performance/fps impact the result. Even at 60 fps at best the accuracy would be within ~17 milliseconds.
- it's pretty slow, a little less than 4 min for a 9 min race


## How to use :
I made an executable version you can download in the [release section](https://github.com/elyetis/nopixel_racevideo_checkpoint/releases).

There is no GUI, so pretty much everything is in command, and I know as a whole it is not very user friendly ( if you don't do what is expected, it will just crash ).
That being said you don't need to do much, and I'll try to automate some of the things the program ask you to input at the start of the program.

# Example :
For a race looking like this :
![ex1](https://i.imgur.com/yqjAGLT.png)
![ex2](https://i.imgur.com/mCQaDaV.png)

This is what you would have written :
![ex3](https://i.imgur.com/Z86tXU4.png)

When asked to "With your mouse left button, select the whole race interface from top left to bottom right then press Enter"
this is what I call the race interface :

![ex3](https://i.imgur.com/BpREiPt.png)
