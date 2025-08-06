import argparse
from typing import Any, Dict, Optional

import numpy as np
import tensorflow as tf
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import Adam


def iris_model() -> Model:
    model = Sequential()
    model.add(Dense(10, input_shape=(4,), activation='relu', name='fc1'))
    model.add(Dense(10, activation='relu', name='fc2'))
    model.add(Dense(3, activation='softmax', name='output'))

    return model


class MetricsPrint(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch: int, logs: Optional[Dict[str, Any]] = None) -> None:
        """
        Simple function for printing the history so that Katib picks it up
        """
        hist: Dict[str, Any] = self.model.history.history
        history_keys: list[str] = list(hist.keys())
        print('\nepoche {}:'.format(epoch))
        for cur_key in history_keys:
            print('{}={}'.format(cur_key, hist[cur_key][-1]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--batch-size',
        type=int,
        default=5,
        help='input batch size for training (default: 5)',
    )
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=0.001,
        help='learning rate (default: 0.001)',
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=100,
        metavar='N',
        help='number of epochs to train (default: 100)',
    )
    args = parser.parse_args(args=[])

    iris_data = load_iris()  # load the iris dataset

    print('Example data: ')
    print(iris_data.data[:5])
    print('Example labels: ')
    print(iris_data.target[:5])

    x: np.ndarray = iris_data.data
    y_: np.ndarray = iris_data.target.reshape(-1, 1)  # Convert data to a single column

    # One Hot encode the class labels
    encoder = OneHotEncoder(sparse_output=False)
    y: np.ndarray = encoder.fit_transform(y_)

    train_x: np.ndarray
    test_x: np.ndarray
    train_y: np.ndarray
    test_y: np.ndarray
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.20)

    model: Model = iris_model()

    # Adam optimizer with learning rate of 0.001
    optimizer = Adam(learning_rate=args.learning_rate)
    model.compile(
        optimizer, loss='categorical_crossentropy', metrics=['accuracy']
    )

    print('Neural Network Model Summary: ')
    print(model.summary())

    # Train the model
    model.fit(
        train_x,
        train_y,
        verbose=0,
        batch_size=args.batch_size,
        epochs=args.epochs,
        callbacks=[MetricsPrint()],
    )


if __name__ == "__main__":
    main()

