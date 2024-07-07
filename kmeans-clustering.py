# given a directory with images, groups them into predefined clusters using KMeans. Uses VGG16 for feature vectors.
path = "/Users/HP/PycharmProjects/pythonProject/test2"
failedPklPath = "/Users/HP/PycharmProjects/pythonProject/dir/fpk.pk"
imageExtension = '.jpg'
noOfClusters = 20

from tqdm import tqdm
# clustering and dimension reduction
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
# for loading/processing the images  
from keras.preprocessing.image import load_img 
from keras.preprocessing.image import img_to_array 
from keras.applications.vgg16 import preprocess_input 

# models 
from keras.applications.vgg16 import VGG16 
from keras.models import Model

# for everything else
import os
import numpy as np
import matplotlib.pyplot as plt
from random import randint
import pandas as pd
import pickle



# change the working directory to the path where the images are located
os.chdir(path)

# this list holds all the image filename
flowers = []

# creates a ScandirIterator aliased as files
with os.scandir(path) as files:
  # loops through each file in the directory
    for file in files:
        if file.name.endswith(imageExtension):
          # adds only the image files to the flowers list
            flowers.append(file.name)

print(len(flowers))

# load the image as a 224x224 array
img = load_img(flowers[0], target_size=(224,224))
# convert from 'PIL.Image.Image' to numpy array
img = np.array(img)

print(img.shape)
(224, 224, 3)

reshaped_img = img.reshape(1,224,224,3)
print(reshaped_img.shape)
(1, 224, 224, 3)

x = preprocess_input(reshaped_img)
def extract_features(file, model):
    # load the image as a 224x224 array
    img = load_img(file, target_size=(224,224))
    # convert from 'PIL.Image.Image' to numpy array
    img = np.array(img) 
    # reshape the data for the model reshape(num_of_samples, dim 1, dim 2, channels)
    reshaped_img = img.reshape(1,224,224,3) 
    # prepare image for model
    imgx = preprocess_input(reshaped_img)
    # get the feature vector
    features = model.predict(imgx, use_multiprocessing=True)
    return features

model = VGG16()
model = Model(inputs = model.inputs, outputs = model.layers[-2].output)


data = {}

# lop through each image in the dataset
for flower in tqdm(flowers, desc="exctracting features"):
    # try to extract the features and update the dictionary
    try:
        feat = extract_features(flower, model)
        data[flower] = feat
        # if (len(data) == 100):
        #   break
    # if something fails, save the extracted features as a pickle file (optional)
    except Exception as e:
        print(e)
        with open(failedPklPath,'wb') as file:
            pickle.dump(data,file)
          
 
# get a list of the filenames
filenames = np.array(list(data.keys()))

# get a list of just the features
feat = np.array(list(data.values()))
feat.shape

# reshape so that there are 210 samples of 4096 vectors
feat = feat.reshape(-1,4096)
feat.shape


pca = PCA(n_components=100, random_state=22)
pca.fit(feat)
x = pca.transform(feat)

kmeans = KMeans(n_clusters=noOfClusters, random_state=22)
kmeans.fit(x)

# holds the cluster id and the images { id: [images] }
groups = {}
for file, cluster in zip(filenames,kmeans.labels_):
    if cluster not in groups.keys():
        groups[cluster] = []
        groups[cluster].append(file)
    else:
        groups[cluster].append(file)

import shutil
from pathlib import Path

for group in groups:
  groupDir = f"{path}clustering/cluster-{str(group)}"
  Path(groupDir).mkdir(parents=True, exist_ok=True)
  for im in groups[group]:
    dest_path = os.path.join(groupDir, im)
    shutil.copy(os.path.join(path, im), dest_path)