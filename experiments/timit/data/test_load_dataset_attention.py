#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import sys
import unittest
import tensorflow as tf

sys.path.append('../../')
sys.path.append('../../../')
from load_dataset_attention import Dataset
from utils.labels.character import num2char
from utils.labels.phone import num2phone


class TestLoadDatasetAttention(unittest.TestCase):

    def test(self):
        self.check_loading(label_type='character', num_gpu=1, is_sorted=True)
        self.check_loading(label_type='character', num_gpu=1, is_sorted=False)
        self.check_loading(label_type='phone61', num_gpu=1, is_sorted=True)
        self.check_loading(label_type='phone61', num_gpu=1, is_sorted=False)

        # self.check_loading(label_type='character', num_gpu=2, is_sorted=True)
        # self.check_loading(label_type='character', num_gpu=2, is_sorted=False)
        # self.check_loading(label_type='phone61', num_gpu=2, is_sorted=True)
        # self.check_loading(label_type='phone61', num_gpu=2, is_sorted=False)

        # For many GPUs
        # self.check_loading(label_type='character', num_gpu=7, is_sorted=True)

    def check_loading(self, label_type, num_gpu, is_sorted):
        print('----- label_type: ' + label_type + ', num_gpu: ' +
              str(num_gpu) + ', is_sorted: ' + str(is_sorted) + ' -----')

        batch_size = 64
        eos_index = 2 if label_type == 'character' else 1
        dataset = Dataset(data_type='train', label_type=label_type,
                          batch_size=batch_size, eos_index=eos_index,
                          is_sorted=is_sorted, is_progressbar=True,
                          num_gpu=num_gpu)

        tf.reset_default_graph()
        with tf.Session().as_default() as sess:
            print('=> Loading mini-batch...')
            if label_type == 'character':
                map_file_path = '../metrics/mapping_files/attention/char2num.txt'
                map_fn = num2char
            else:
                map_file_path = '../metrics/mapping_files/attention/phone2num_' + \
                    label_type[5:7] + '.txt'
                map_fn = num2phone

            mini_batch = dataset.next_batch(session=sess)

            iter_per_epoch = int(dataset.data_num /
                                 (batch_size * num_gpu)) + 1
            for i in range(iter_per_epoch + 1):
                return_tuple = mini_batch.__next__()
                inputs = return_tuple[0]
                labels = return_tuple[1]
                labels_seq_len = return_tuple[3]

                if num_gpu > 1:
                    for inputs_gpu in inputs:
                        print(inputs_gpu.shape)
                    inputs = inputs[0]
                    labels = labels[0]
                    labels_seq_len = labels_seq_len[0]

                str_true = map_fn(
                    labels[0][0: labels_seq_len[0]], map_file_path)
                str_true = re.sub(r'_', ' ', str_true)
                print(str_true)


if __name__ == '__main__':
    unittest.main()
