import cv2
import numpy as np
import os
import sys
import math
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    #First, we declare our auxiliary variables. Our output lists and size
    images = []
    labels = []
    size = (IMG_WIDTH,IMG_HEIGHT)
    n_img = 0
    m_img = 0
    #Let's count the images so we can make a "loading images" percentage bar
    for subdir in os.listdir(data_dir):
        for filename in os.listdir( os.path.join(data_dir,subdir) ):
            n_img+=1
    
            
    #Then we read the images. First each folder and then each image in a given
    #folder. We resize them inmediately and add them to our array with its
    #corresponding label (Which is equivalent to the folder it's in)
    for subdir in os.listdir(data_dir):
        for filename in os.listdir( os.path.join(data_dir,subdir) ):
            img = cv2.imread( os.path.join(data_dir,subdir,filename) )
            img = cv2.resize(img,size)
            if img is not None:
                images.append(img)
                labels.append(subdir)
                m_img += 1
        print("Image reading: " + str(math.floor(m_img/n_img*100))+"%")
    #Finally, we put our lists in a tuple and return it.
    return (images,labels)
    


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    #First things first, we declare aux variables and initialize our sequential model
    size = (IMG_WIDTH, IMG_HEIGHT, 3)
    
    model = tf.keras.models.Sequential([
        
        #Convolutional layer to get the image. Doing a little research, 3d convs
        #are usually best suited for video processing, so we stick to the 2dconv
        tf.keras.layers.Conv2D(
            32, (3,3), activation="relu",input_shape=size
            ),
        
        #Next, max-pooling. We'll use a small filter to void loosing too many
        #pixels
        tf.keras.layers.MaxPooling2D(pool_size=(2,2)),
        
        #We'll leave this space to add another conv+pool layer later
        tf.keras.layers.Conv2D(
            32, (3,3), activation="relu",input_shape=size
            ),
        #tf.keras.layers.MaxPooling2D(pool_size=(2,2)),
        
        #Flattening like a pizza dough
        tf.keras.layers.Flatten(),
        
        #Let's get to our dense layers. Let's start small, pointing to an
        #Occam's Razor resolution. If we get a bad classification, we'll 
        #plug more neurons. (We have 15x15=225 pixels, let's start with 64 neurons)
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.3),
        #Finally, our output layer with softmax so we get a probability, which
        #servers our purposes just right.
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
        ])
    
    #We compile our model
    model.compile(
        optimizer = "adam",
        loss = "categorical_crossentropy",
        metrics = ["accuracy"]
        )
    
    #Finally, return this bad boy
    return model
    
    


if __name__ == "__main__":
    main()
