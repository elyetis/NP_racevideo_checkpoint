This program allow you to get sector time from a video a race by analysing said video with Pysseract.
Ideal scenario would be someone making some shared google sheet with different racer PB / LR etc.

##Important :
- probably only properly works on *936p* video at the moment ( this is what happen when you only use neutren and Sarah_Digitally video during your tests... ), it should likely works on 1080/720p too *if there is no phone notification on screen during the race*, that being said I'll probably solve that limitation in the next few days
- that being said 720p might never properly work, lower resolution might make it too hard for proper text recognition I don't know yet
- don't expect ultra high accuracy, performance/fps impact the result. Even at 60 fps at best the accuracy would be within ~17 milliseconds.

##How to use :
There is no GUI, so everything is in command, and I know as a whole it is not very user friendly ( if you don't do what is expected, it will just crash ).
That being said you don't need to do much, and I'll try to automate some of the things the program ask you to input at the start of the program.

#Example :
For a race looking like this :
![ex1](https://i.imgur.com/yqjAGLT.png)
![ex2](https://i.imgur.com/mCQaDaV.png)
This is what you would have written :
![ex3](https://i.imgur.com/Z86tXU4.png)

When asked to "With your mouse left button, select the whole race interface from top left to bottom right then press Enter"
this is what I call the race interface :

![ex3](https://i.imgur.com/BpREiPt.png)
