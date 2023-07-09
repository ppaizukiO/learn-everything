# -*- coding: utf-8 -*-
"""MAGIC_Gamma_Telescope

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nxyJd6A35CafV6bAq03xF_lbwD1sd2MV
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import RandomOverSampler

cols = ["fLength", "fWidth", "fSize", "fConc", "fConc1", "fAsym", "fM3Long", "fM3Trans", "fAlpha", "fDist", "class"]
df = pd.read_csv("magic04.data", names = cols)
df.head()

"""^var_name^.read_csv("***") reads the data from the csv file given in place of '***'
**.head() displays the first five rows of the data
"""

# df["class"].unique()  # .unique() finds the unique elements in an array and displays them in a sorted array
df["class"] = (df["class"] == "g").astype(int)

"""in the above cell, if the element in the class is equal to g, it is turned into 1 otherwise 0 because computers understands numbers better than letters"""

for label in cols[:-1]:
  plt.hist(df[df["class"]==1][label], color="blue", label="gamma", alpha=0.7, density=True)
  plt.hist(df[df["class"]==0][label], color="red", label="hadron", alpha=0.7, density=True)
  plt.title(label)
  plt.ylabel("probablity")
  plt.xlabel(label)
  plt.legend()
  plt.show()

"""#train, validation and test datasets"""

train, val, test = np.split(df.sample(frac=1), [int(0.6*len(df)), int(0.8*len(df))])

"""this splits the dataset into training, validation and test datasets. training set is 60% and validation set is 20% (from 60 to 80). test set is the remaining 20% after the validation set.

The sample() method returns a list with a randomly selection of a specified number of items from a sequnce
"""

def scale_dataset(dataframe,oversample=False):
  X = dataframe[dataframe.columns[:-1]].values
  y = dataframe[dataframe.columns[-1]].values

  scaler = StandardScaler()
  X = scaler.fit_transform(X)

  if oversample:
    ros = RandomOverSampler()
    X,y = ros.fit_resample(X,y)

  data = np.hstack((X, np.reshape(y, (-1,1))))
  return data, X, y

train, X_train, y_train = scale_dataset(train, oversample=True)
val, X_val, y_val = scale_dataset(val, oversample=False)
test, X_test, y_test = scale_dataset(test, oversample=False)

#len(y_train)
#sum(y_train == 1)
#sum(y_train == 0)

"""#KNN
K-Nearest Neighbours

uses euclidian distance formaula

d = ((x1 - x2)^2 + (y1 - y2)^2)^1/2

k is the variable that says how many neighbours are being used to determine the label.
"""

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report

knn_model = KNeighborsClassifier(n_neighbors = 1)
knn_model.fit(X_train, y_train)

y_pred = knn_model.predict(X_test)
print(classification_report(y_test, y_pred))

"""#Naive Bayes"""

from sklearn.naive_bayes import GaussianNB

nb_model = GaussianNB()
nb_model = nb_model.fit(X_train,y_train)

y_pred = nb_model.predict(X_test)
print(classification_report(y_test, y_pred))

"""#log regression"""

from sklearn.linear_model import LogisticRegression

lg_model = LogisticRegression()
lg_model = lg_model.fit(X_train, y_train)

y_pred = lg_model.predict(X_test)
print(classification_report(y_test, y_pred))

"""#Support Vector Machine"""

from sklearn.svm import SVC

svm_model = SVC()
svm_model = svm_model.fit(X_train, y_train)

y_pred = svm_model.predict(X_test)
print(classification_report(y_test, y_pred))

"""#neural networks"""

import tensorflow as tf

def plot_history(history):
  fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
  ax1.plot(history.history['loss'], label='loss')
  ax1.plot(history.history['val_loss'], label='val_loss')
  ax1.set_xlabel('Epoch')
  ax1.set_ylabel('Binary crossentropy')
  ax1.grid(True)

  ax2.plot(history.history['accuracy'], label='accuracy')
  ax2.plot(history.history['val_accuracy'], label='val_accuracy')
  ax2.set_xlabel('Epoch')
  ax2.set_ylabel('Accuracy')
  ax2.grid(True)

  plt.show()

def train_model(X_train, y_train, num_nodes, dropout_prob, lr, batch_size, epochs):
  nn_model = tf.keras.Sequential([
      tf.keras.layers.Dense(num_nodes, activation='relu', input_shape=(10,)),
      tf.keras.layers.Dropout(dropout_prob),
      tf.keras.layers.Dense(num_nodes, activation='relu'),
      tf.keras.layers.Dropout(dropout_prob),
      tf.keras.layers.Dense(1, activation='sigmoid')
  ])

  nn_model.compile(optimizer=tf.keras.optimizers.Adam(lr), loss='binary_crossentropy',
                  metrics=['accuracy'])
  history = nn_model.fit(
    X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=0
  )

  return nn_model, history

least_val_loss = float('inf')
least_loss_model = None
epochs = 100

for num_nodes in [16, 32, 64]:
    for dropout_prob in [0, 0.2]:
        for lr in [0.01, 0.005, 0.001]:
            for batch_size in [32, 64, 128]:
                print(f"{num_nodes} nodes, dropout {dropout_prob}, lr {lr}, batch size {batch_size}")
                model, history = train_model(X_train, y_train, num_nodes, dropout_prob, lr, batch_size, epochs)
                plot_history(history)
                val_loss = model.evaluate(X_val, y_val)[0]  # Extract the appropriate loss value
                if val_loss < least_val_loss:
                    least_val_loss = val_loss
                    least_loss_model = model

y_pred = least_loss_model.predict(X_test)
y_pred = (y_pred > 0.5).astype(int)
y_pred