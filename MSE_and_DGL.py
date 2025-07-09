#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  9 14:49:56 2025

@author: ERASMUSMC+109098
"""
# Gradient difference loss + MSE (weights of both functions are 50/50)

import tensorflow.keras as keras 
import tensorflow as tf
import numpy as np


class MSE_and_GDL(tf.keras.losses.Loss):
    def __init__(self, lambda_mse=1.0, lambda_gdl=1.0, name="MSE_and_GDL"):
        super().__init__(name=name)
        self.lambda_mse = lambda_mse
        self.lambda_gdl = lambda_gdl
        self.mse_fn = tf.keras.losses.MeanSquaredError()

    def call(self, y_true, y_pred):
        mse = self.mse_fn(y_true, y_pred)

        grad_diff_z = tf.math.squared_difference(
            y_pred[:, 1:, :, :, :] - y_pred[:, :-1, :, :, :],
            y_true[:, 1:, :, :, :] - y_true[:, :-1, :, :, :]
        )
        grad_diff_y = tf.math.squared_difference(
            y_pred[:, :, 1:, :, :] - y_pred[:, :, :-1, :, :],
            y_true[:, :, 1:, :, :] - y_true[:, :, :-1, :, :]
        )
        grad_diff_x = tf.math.squared_difference(
            y_pred[:, :, :, 1:, :] - y_pred[:, :, :, :-1, :],
            y_true[:, :, :, 1:, :] - y_true[:, :, :, :-1, :]
        )

        loss = (self.lambda_mse * mse + self.lambda_gdl * (tf.reduce_sum(grad_diff_z) +
                                   tf.reduce_sum(grad_diff_y) +
                                   tf.reduce_sum(grad_diff_x))) / tf.cast(tf.size(y_pred, out_type=tf.int32), tf.float32)

        return loss

# Different possiblities to sum, normalize etc. 
# Change the weights of lambda for optimization!