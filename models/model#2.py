import numpy as np
import os
from data_processing.general_processor import Utils
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use("TkAgg")
from sklearn.preprocessing import StandardScaler # Usare MIn MAx scaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import minmax_scale
import tensorflow as tf

physical_devices = tf.config.experimental.list_physical_devices('GPU')
assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
config = tf.config.experimental.set_memory_growth(physical_devices[0], True)

#Check dll library
# tf.test.gpu_device_name()

"""
Load only and split
"""

dir_path = "D:\\datasets\\eeg_dataset"
#Load data
x_data = np.load(os.path.join(dir_path, "x_C3_C4.npy"))
y = np.load(os.path.join(dir_path, "y_C3_C4.npy"))
x_data = Utils.cut_width(x_data)
#Scale
#reshape (18511,1280)
x_data_resh = x_data.reshape(x_data.shape[0], x_data.shape[2]*x_data.shape[1])


# x_data_scale = MinMaxScaler().fit_transform(x_data_mono) #Fare MinMax Scare, portare tra 0 e 1
x_data_scale = minmax_scale(x_data_resh, axis=1)


# import matplotlib
# matplotlib.use("TkAgg")
# import matplotlib.pyplot as plt
# plt.subplot(1,2,1)
# plt.plot(x_data[0][0])
# plt.show()
# plt.subplot(1,2,2)
# plt.plot(x_data_scale[0][:640])
# plt.show()

x_resh = x_data_scale.reshape(x_data_scale.shape[0], x_data_scale.shape[1], 1)

y_resh = y.reshape(y.shape[0], 1)
y_categorical = tf.keras.utils.to_categorical(y_resh, 5)
x_train, x_test, y_train, y_test = train_test_split(x_resh, y_categorical, stratify=y_categorical, test_size=0.10, random_state=56)

def get_distribution(y_train, y_test, n):
    for x in range(n):
        array = np.zeros(n)
        array[x] = 1
        print("Class: " + str(x) +
              " Train: " + str(len([y for y in y_train if np.all(y == np.array(array))])) +
              " Test: " + str(len([y for y in y_test if np.all(y == np.array(array))])))

get_distribution(y_train, y_test, 5)


#%%
#Convolution Neural Network
# [samples, time steps, features].
# real_x_train = x_train.reshape(14808, 640, 2)
# real_x_test = x_test.reshape(3703, 640, 2)
learning_rate = 1e-4 # default 1e-3
kernel_size = 3
drop_rate = 0.5
batch_size = 10

model = tf.keras.Sequential()
model.add(tf.keras.layers.Conv1D(filters=32, kernel_size=kernel_size, activation='relu', padding= "same", input_shape=(1280, 1)))
model.add(tf.keras.layers.AvgPool1D(pool_size=2))
model.add(tf.keras.layers.Conv1D(filters=32, kernel_size=kernel_size, activation='relu', padding= "same"))
model.add(tf.keras.layers.AvgPool1D(pool_size=2))
model.add(tf.keras.layers.Conv1D(filters=32, kernel_size=kernel_size, activation='relu', padding= "same"))
model.add(tf.keras.layers.AvgPool1D(pool_size=2))
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(1024, activation='relu'))
model.add(tf.keras.layers.Dropout(drop_rate))
model.add(tf.keras.layers.Dense(512, activation='relu'))
model.add(tf.keras.layers.Dropout(drop_rate))
model.add(tf.keras.layers.Dense(5, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer=tf.keras.optimizers.Adam(lr=learning_rate), metrics=['accuracy'])
model.summary()
history = model.fit(x_train, y_train, epochs=100, batch_size=batch_size, steps_per_epoch=x_train.shape[0]/batch_size,
                    shuffle=True, validation_data=(x_test,y_test))



