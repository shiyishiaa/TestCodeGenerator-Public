import unittest

from util import extract_code_blocks


class TestUtilCode(unittest.TestCase):
    invalid_code = "'The image appears to be a stylized audio waveform or spectrogram, likely representing sound frequencies and their amplitudes over time. The colors transition from teal to yellow and then to red, indicating varying sound intensities or frequencies. The vertical bars represent different frequency bands, and their heights correspond to the amplitude or strength of the sound at those frequencies. The overall design is modern and visually appealing, suitable for audiovisual applications or music visualization. If you have specific questions about this image or its context, feel free to ask!'"

    def test_extract_code_blocks_invalid_code(self):
        code_blocks = extract_code_blocks(self.invalid_code)
        print(code_blocks)
        self.assertEqual(len(code_blocks), 1)


if __name__ == "__main__":
    unittest.main()
