# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.
# ==============================================================================
"""Tests for ImageIOTensor."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np

import tensorflow as tf
import tensorflow_io as tfio

def test_tiff_io_tensor():
  """Test case for TIFFImageIOTensor"""
  width = 560
  height = 320
  channels = 4

  images = []
  for filename in [
      "small-00.png",
      "small-01.png",
      "small-02.png",
      "small-03.png",
      "small-04.png"]:
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "test_image",
                     filename), 'rb') as f:
      png_contents = f.read()
    image_v = tf.image.decode_png(png_contents, channels=channels)
    assert image_v.shape == [height, width, channels]
    images.append(image_v)

  filename = os.path.join(
      os.path.dirname(os.path.abspath(__file__)), "test_image", "small.tiff")
  filename = "file://" + filename

  tiff = tfio.IOTensor.from_tiff(filename)
  assert tiff.keys == list(range(5))
  for i in tiff.keys:
    assert np.all(images[i].numpy() == tiff(i).to_tensor().numpy())

def test_decode_webp():
  """Test case for decode_webp."""
  width = 400
  height = 301
  channel = 4
  png_file = os.path.join(
      os.path.dirname(os.path.abspath(__file__)), "test_image", "sample.png")
  with open(png_file, 'rb') as f:
    png_contents = f.read()
  filename = os.path.join(
      os.path.dirname(os.path.abspath(__file__)), "test_image", "sample.webp")
  with open(filename, 'rb') as f:
    webp_contents = f.read()

  png = tf.image.decode_png(png_contents, channels=channel)
  assert png.shape == (height, width, channel)

  webp_v = tfio.image.decode_webp(webp_contents)
  assert webp_v.shape == (height, width, channel)

  assert np.all(webp_v == png)


def test_tiff_file_dataset():
  """Test case for TIFFDataset."""
  width = 560
  height = 320
  channels = 4

  images = []
  for filename in [
      "small-00.png",
      "small-01.png",
      "small-02.png",
      "small-03.png",
      "small-04.png"]:
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "test_image",
                     filename), 'rb') as f:
      png_contents = f.read()
    image_v = tf.image.decode_png(png_contents, channels=channels)
    assert image_v.shape == [height, width, channels]
    images.append(image_v)

  filename = os.path.join(
      os.path.dirname(os.path.abspath(__file__)), "test_image", "small.tiff")
  filename = "file://" + filename

  num_repeats = 2

  dataset = tfio.experimental.IODataset.from_tiff(filename).repeat(num_repeats)
  i = 0
  for v in dataset:
    np.all(images[i % 5] == v)
    i += 1
  assert i == 10

def test_draw_bounding_box():
  """Test case for draw_bounding_box."""
  width = 560
  height = 320
  channels = 4

  with open(
      os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "test_image",
                   "small-00.png"), 'rb') as f:
    png_contents = f.read()
  with open(
      os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "test_image",
                   "small-bb.png"), 'rb') as f:
    ex_png_contents = f.read()
  ex_image_p = tf.image.decode_png(ex_png_contents, channels=channels)
  # TODO: Travis seems to have issues with different rendering. Skip for now.
  # ex_image_v = ex_image_p.eval()
  _ = tf.expand_dims(ex_image_p, 0)

  bb = [[[0.1, 0.2, 0.5, 0.9]]]
  image_v = tf.image.decode_png(png_contents, channels=channels)
  assert image_v.shape == (height, width, channels)
  image_p = tf.image.convert_image_dtype(image_v, tf.float32)
  image_p = tf.expand_dims(image_p, 0)
  bb_image_p = tfio.experimental.image.draw_bounding_boxes(
      image_p, bb, ["hello world!"])
  # TODO: Travis seems to have issues with different rendering. Skip for now.
  # self.assertAllEqual(bb_image_v, ex_image_v)
  _ = tf.image.convert_image_dtype(bb_image_p, tf.uint8)

def test_decode_ppm():
  """Test case for decode_ppm"""
  ppm_file = os.path.join(
      os.path.dirname(os.path.abspath(__file__)),
      "test_image", "r-1316653631.481244-81973200.ppm")
  png_file = os.path.join(
      os.path.dirname(os.path.abspath(__file__)),
      "test_image", "r-1316653631.481244-81973200.png")
  ppm = tfio.experimental.image.decode_pnm(tf.io.read_file(ppm_file))
  png = tf.image.decode_png(tf.io.read_file(png_file))
  assert np.all(ppm.numpy() == png.numpy())

  pgm_file = os.path.join(
      os.path.dirname(os.path.abspath(__file__)),
      "test_image", "d-1316653631.269651-68451027.pgm")
  png_file = os.path.join(
      os.path.dirname(os.path.abspath(__file__)),
      "test_image", "d-1316653631.269651-68451027.png")
  pgm = tfio.experimental.image.decode_pnm(
      tf.io.read_file(pgm_file), dtype=tf.uint16)
  png = tf.image.decode_png(tf.io.read_file(png_file), dtype=tf.uint16)
  assert np.all(pgm.numpy() == png.numpy())

def test_encode_webp():
  """Test case for encode_bmp."""
  width = 51
  height = 26
  channels = 3
  bmp_file = os.path.join(
      os.path.dirname(os.path.abspath(__file__)), "test_image", "lena.bmp")
  with open(bmp_file, 'rb') as f:
    bmp_contents = f.read()
  image_v = tf.image.decode_bmp(bmp_contents)
  assert image_v.shape == [height, width, channels]
  bmp_encoded = tfio.image.encode_bmp(image_v)
  image_e = tf.image.decode_bmp(bmp_encoded)
  assert np.all(image_v.numpy() == image_e.numpy())

def test_decode_exif():
  """Test case for decode_exif."""
  jpeg_file = os.path.join(
      os.path.dirname(os.path.abspath(__file__)),
      "test_image", "down-mirrored.jpg")
  exif = tfio.experimental.image.decode_jpeg_exif(tf.io.read_file(jpeg_file))
  assert exif == 4

def test_openexr_io_tensor():
  """Test case for OpenEXRIOTensor"""
  # image from http://gl.ict.usc.edu/Data/HighResProbes/
  filename = os.path.join(
      os.path.dirname(os.path.abspath(__file__)),
      "test_image", "glacier.exr")
  filename = "file://" + filename

  exr_shape, exr_dtype, exr_channel = tfio.experimental.image.decode_exr_info(
      tf.io.read_file(filename))
  assert np.all(exr_shape == [1024, 2048])
  assert np.all(exr_dtype.numpy() == [tf.float16, tf.float16, tf.float16])
  assert np.all(exr_channel == ['B', 'G', 'R'])

  exr_0_b = tfio.experimental.image.decode_exr(
      tf.io.read_file(filename), 0, 'B', tf.float16)
  exr_0_g = tfio.experimental.image.decode_exr(
      tf.io.read_file(filename), 0, 'G', tf.float16)
  exr_0_r = tfio.experimental.image.decode_exr(
      tf.io.read_file(filename), 0, 'R', tf.float16)

  exr = tfio.experimental.IOTensor.from_exr(filename)
  assert exr.keys == [0]
  assert exr(0).columns == ['B', 'G', 'R']

  assert exr(0)('B').dtype == tf.float16
  assert exr(0)('G').dtype == tf.float16
  assert exr(0)('R').dtype == tf.float16

  assert exr(0)('B').shape == [1024, 2048]
  assert exr(0)('G').shape == [1024, 2048]
  assert exr(0)('R').shape == [1024, 2048]

  b = exr(0)('B').to_tensor()
  g = exr(0)('G').to_tensor()
  r = exr(0)('R').to_tensor()

  assert b.shape == [1024, 2048]
  assert g.shape == [1024, 2048]
  assert r.shape == [1024, 2048]

  assert b.dtype == tf.float16
  assert g.dtype == tf.float16
  assert r.dtype == tf.float16

  rgb = tf.stack([r, g, b], axis=2)
  rgb = tf.image.convert_image_dtype(rgb, tf.uint8)
  _ = tf.image.encode_png(rgb)
  # TODO: compare with generated png
  # tf.io.write_file('sample.png', png)

  assert np.all(b == exr_0_b)
  assert np.all(g == exr_0_g)
  assert np.all(r == exr_0_r)


if __name__ == "__main__":
  test.main()
