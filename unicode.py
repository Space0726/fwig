""" 클래스 인자로 유니코드(16진수, 10진수 상관없이) 숫자를 넣어주면 해당하는 글자의 구성요소를 얻을 수 있음

초성: first_char, 중성: middle_char, 종성: final_char
0xAC00: '가' ~ 0xD7A3: '힣'

Last Modified Date: 2019/10/21

Created by Seongju Woo.
"""
class Uni2Kor():
    """ Convert unicode to Hangul(Korean) characters.

    Examples:
        uc = Uni2Char(0xAC00)
        print(uc) # 글자 구성요소 출력 -> 'AC00: ㄱ + ㅏ'

        # Two usages.
        Uni2Char(0xAC00).get_chars()    # Save characters information to object.
        Uni2Char().get_chars(0xAC00)    # Doesn't save, just convert it.
    """
    # 588개씩
    first = {
        0:'ㄱ', 1:'ㄲ', 2:'ㄴ', 3:'ㄷ', 4:'ㄸ', 5:'ㄹ', 6:'ㅁ', 7:'ㅂ', 8:'ㅃ', 9:'ㅅ', 10:'ㅆ',
        11:'ㅇ', 12:'ㅈ', 13:'ㅉ', 14:'ㅊ', 15:'ㅋ', 16:'ㅌ', 17:'ㅍ', 18:'ㅎ'
    }
    # 28개씩
    middle = {
        0:'ㅏ', 1:'ㅐ', 2:'ㅑ', 3:'ㅒ', 4:'ㅓ', 5:'ㅔ', 6:'ㅕ', 7:'ㅖ', 8:'ㅗ', 9:'ㅘ', 10:'ㅙ',
        11:'ㅚ', 12:'ㅛ', 13:'ㅜ', 14:'ㅝ', 15:'ㅞ', 16:'ㅟ', 17:'ㅠ', 18:'ㅡ', 19:'ㅢ', 20:'ㅣ'
    }
    # 28개씩
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
        return hex(self.code).upper()[2:] + ': ' \
               + self.first_char + ' + ' \
               + self.middle_char + ' + ' \
               + self.final_char

    def get_hex_code(self):
        """ Returns Unicode in hexadecimal format. """
        if self.code is None:
            return ""
        return hex(self.code).upper()[2:]

    def get_chars(self, code=None):
        """ Returns characters that converted from unicode. """
        if code is None:
            return [self.first_char, self.middle_char, self.final_char]
        first_idx = (code - 0xAC00) // 588
        middle_idx = (code - 0xAC00 - 588*first_idx) // 28
        final_idx = (code - 0xAC00) % 28
        return [Uni2Char.first[first_idx], Uni2Char.middle[middle_idx], Uni2Char.final[final_idx]]

    def get_char_dict(self, to_hex=False):
        """ 유니코드 및 글자 구성요소들을 딕셔너리 자료형으로 리턴 """
        if self.code is None:
            return {}
        if to_hex:
            return {self.get_hex_code(): [self.first_char, self.middle_char, self.final_char]}
        return {self.code: [self.first_char, self.middle_char, self.final_char]}
