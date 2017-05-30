import binary2DICOM as b2d
import numpy as np

import unittest


# Here's our "unit tests".
class MakeGradientTest(unittest.TestCase):

    def test_make_gradient_2d(self):
        """
        Function creates a dummy file with a 2D gradient.
        :return: True
        """
        print('[INFO] Making 2d image filled with gradient squares.')
        x = np.arange(16).reshape(16,1) # tworzymy gradient 1D
        pixel_array = (x + x.T) * 16 # z tablicy robimy gradient 2D i wygladzamy
        pixel_array = np.tile(pixel_array,(4,4)) # powielamy 4 razy wzdluz X i Y
        b2d.write_dicom({'out_file':'pretty2d.dcm', 'bytes_per_pix':1, 'is_signed':False, 'is_float':False}, pixel_array)
        self.assertTrue(True)

    def test_make_gradient_3d(self):
        """
        Function creates a dummy file with a 2D gradient, repeated on 4 slices.
        :return: 
        """
        print('[INFO] Making 3d image filled with gradient squares.')
        x = np.arange(16).reshape(16, 1)  # tworzymy gradient 1D
        pixel_array = (x + x.T) * 16  # z tablicy robimy gradient 2D i wygladzamy
        pixel_array = np.tile(pixel_array, (4, 4, 4))
        b2d.write_dicom({'out_file':'pretty2d.dcm', 'bytes_per_pix':1, 'is_signed':False, 'is_float':False}, pixel_array)
        self.assertTrue(True)


def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()
