""" Convert unicode to character and letter components.

초성: first_char, 중성: middle_char, 종성: final_char
0xAC00: '가' ~ 0xD7A3: '힣'

Last Modified Date: 2019/10/21

Created by Seongju Woo.
"""
class Uni2Kor():
    """ Convert unicode to Hangul(Korean) characters.

    Args:
        code:: int (default is None)
            A unicode value in Korean range. (0xAC00 ~ 0xD7A3)

    Examples:
        >>> uc = Uni2Char(0xAC00)
        >>> uc    # Print letter components
        'AC00: ㄱ + ㅏ'
        >>> Uni2Char(0xAC00).get_chars()    # Save characters information to object.
        ['ㄱ', 'ㅏ', None]
        >>> Uni2Char().get_chars(0xAC00)    # Doesn't save, just convert it.
        ['ㄱ', 'ㅏ', None]
    """
    # 588 each
    first = {
        0:'ㄱ', 1:'ㄲ', 2:'ㄴ', 3:'ㄷ', 4:'ㄸ', 5:'ㄹ', 6:'ㅁ', 7:'ㅂ', 8:'ㅃ', 9:'ㅅ', 10:'ㅆ',
        11:'ㅇ', 12:'ㅈ', 13:'ㅉ', 14:'ㅊ', 15:'ㅋ', 16:'ㅌ', 17:'ㅍ', 18:'ㅎ'
    }
    # 28 each
    middle = {
        0:'ㅏ', 1:'ㅐ', 2:'ㅑ', 3:'ㅒ', 4:'ㅓ', 5:'ㅔ', 6:'ㅕ', 7:'ㅖ', 8:'ㅗ', 9:'ㅘ', 10:'ㅙ',
        11:'ㅚ', 12:'ㅛ', 13:'ㅜ', 14:'ㅝ', 15:'ㅞ', 16:'ㅟ', 17:'ㅠ', 18:'ㅡ', 19:'ㅢ', 20:'ㅣ'
    }
    # 28 each
    final = {
        0:None, 1:'ㄱ', 2:'ㄲ', 3:'ㄱㅅ', 4:'ㄴ', 5:'ㄴㅈ', 6:'ㄴㅎ', 7:'ㄷ', 8:'ㄹ', 9:'ㄹㄱ',
        10:'ㄹㅁ', 11:'ㄹㅂ', 12:'ㄹㅅ', 13:'ㄹㅌ', 14:'ㄹㅍ', 15:'ㄹㅎ', 16:'ㅁ', 17:'ㅂ', 18:'ㅂㅅ',
        19:'ㅅ', 20:'ㅆ', 21:'ㅇ', 22:'ㅈ', 23:'ㅊ', 24:'ㅋ', 25:'ㅌ', 26:'ㅍ', 27:'ㅎ'
    }

    def __init__(self, code=None):
       self.code = code
       if self.code is None:
           self.first_char, self.middle_char, self.final_char = None, None, None
       else:
           self.first_char, self.middle_char, self.final_char = self.get_chars(self.code)

    def __repr__(self):
        if self.code is None:
            return ""
        return '(' + hex(self.code).upper()[2:] + ': ' \
               + self.first_char + ' + ' \
               + self.middle_char + ' + ' \
               + self.final_char + ')'

    @classmethod
    def get_sound(self, sound_name, value):
        """ Return sound character that matched with value.

        Args:
            sound_name:: str
                The name of sound. It will be 'first', 'middle' or 'final'.

            value:: int
                It is the result of calculating Unicode with Korean characters for each sound.
                See the Uni2Kor class' field dictionary.

        Returns:
            matched character:: str

        Examples:
            >>> Uni2Kor.get_sound('first', 0)
            'ㄱ'
        """
        if sound_name == 'first':
            return self.first[value]
        elif sound_name == 'middle':
            return self.middle[value]
        elif sound_name == 'final':
            return self.final[value]
        else:
            raise ValueError("Invalid sound name")

    def get_hex_code(self):
        """ Returns Unicode in hexadecimal format.

        Returns:
            unicode in hexadecimal format:: str
        """
        if self.code is None:
            return ""
        return hex(self.code).upper()[2:]

    def get_chars(self, code=None):
        """ Returns letter component of character that converted from unicode.

        Args:
            code:: int (default is None)
                A unicode that you want to convert.

        Returns:
            letter component of character:: [str, str, str(or None)]
        """
        if code is None:
            return [self.first_char, self.middle_char, self.final_char]
        first_idx = (code - 0xAC00) // 588
        middle_idx = (code - 0xAC00 - 588*first_idx) // 28
        final_idx = (code - 0xAC00) % 28
        return [Uni2Kor.first[first_idx], Uni2Kor.middle[middle_idx], Uni2Kor.final[final_idx]]

    def get_char_dict(self, to_hex=False):
        """ Returns dictionary of unicode and letter component

        Args:
            to_hex:: bool (default is False)
                True if you want to return unicode in hexadecimal, otherwise False

        Returns:
            unicode(keys) and letter component(values):: { str: [str, str, str(or None)] }
        """
        if self.code is None:
            return {}
        if to_hex:
            return {self.get_hex_code(): [self.first_char, self.middle_char, self.final_char]}
        return {self.code: [self.first_char, self.middle_char, self.final_char]}
