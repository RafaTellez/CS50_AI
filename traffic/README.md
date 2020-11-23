  ------------------------------------------------------------------------
  
First Model (m0) 
First approach was to play with the NN hyperparameters,
  so I used the following architecture: 
-Conv2D: 16 (3x3) filters with
  relu 
-MaxPooling: 2x2 kernel 
-Flatten 
-Dense: 64 neurons with relu
  
-Dropout: 0.3 or 30% 
-Dense: NUM\_CATEGORIES neurons (or 43 for gtsrb)
  with softmax 

Optimizer: Adam, 
Loss: Categorical\_Crossentropy, 
Metrics:
  Accuracy 

Results were terrible, around 5% accuracy.
  

------------------------------------------------------------------------
  
Second Model (m1)

  
Tried duplicating the number of filters for the Conv2D layer and
  duplicating the number of neurons in the dense layer, but the result was
  just as awful.
 
 
------------------------------------------------------------------------


Third Model (m2)


Adding an aditional Conv2D+MaxPooling layer incredibly boosted the
 accuracy to over 94% which is pretty good. 
Now I'll tweak it a little 
bit more to see if we can get approximate results with a simpler 
architecture.


-----------------------------------------------------------------------------------------------

Fourth model (m3)


Removing a hidden layer only dropped accuracy by around 5%, but since we 
prefer having 1/20 signs missclassified instead of 1/10, 
we will stick
 to the previous architecture. Also, since we're applying two sets of
 conv+pool to 30x30 pixel images, it isn't really that intensive. 
I tried 
adding the hidden layer back and reduce the ammount of neurons by layer
to 32 instead of 64, this was a terrible idea since we dropped back to
 5% acc.



Increasing the number of neurons actually dropped the acc about 10%. So 
our next test will be two 64 dense layers and add a 3rd conv+pool
filter.


----------------------------------------------------------------------------------------------------

Fifth Model (m4)


Adding a third conv+pool or just a conv layer dropped the acc to about
75%. Maybe the image is too small after the second conv+pool layer to
keep reducing it,
thus making it harder for the NN to learn from it. 
Also, reading the image as a grayscale also dropped the accuracy, 
probably since it has problems 
diferentiating yellow from white and 
red/blue from black, which is fundamental when reading traffic signs, since they're color coded.


----------------------------------------------------------------------------------------------------

Sixth Model (m5)


Just as the second model (m1) but removing the last pooling layer, since
 it would make the image about 7x7 pixels which is too small. 
There's a 
HUGE accuracy boost from the very first epochs, giving us a final 
accuracy of about 94%. Obviously the results vary since 
we're using
 stochastic gradient descent and since dropout is also random.




CONCLUSION 
I like to see Neural Networks as a construction site. Sure 
labor force is important (neurons) but the best way to work is having 
a 
good organization (architecture) in order to do the job in the best 
possible way while keeping the workload balanced and thus, 
making the
 building (training) more efficient. 

Having more neurons and layers sure help a little bit, but they also make the 
whole network 
a lot more intensive. It's better to have just enough neurons 
and layers to do the job, since the largest part of the accuracy comes from

choosing the best configuration in the sequence of layers. For example, 
only one Conv+Pool layer wasn't enough for the NN to discern 
the 
patterns it needed in order to make a good prediction, and three were
 too many.
