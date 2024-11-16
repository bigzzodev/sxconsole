import hashlib

# -----------------------------------------------------------------------------------------------------------------
def rag_db_namespace(_name):

    # 'Hello | World + 한글 - "Test"'
    def fix_query(_naver_query):
        hash_bytes = hashlib.sha256(_naver_query.encode()).digest()
        out =  bytes(a ^ b ^ c ^ d for a, b, c, d in zip(hash_bytes[:8], hash_bytes[8:16], hash_bytes[16:24], hash_bytes[24:]))
        return out.hex()

    if _name == '진민호':
        return fix_query(_name)
    if _name == 'god':
        naver = '지오디 | god'
        return fix_query(naver)
    if _name == '휘성':
        return fix_query(_name)
    ##
    if _name == '이루':
        naver = '가수 이루 -"이루 다" -"이루 말할" -"이루 말로" -"이루 다할" -"이루 셀" -"이루 헤아릴" -"이루 형언할"'
        return 'bc57de0abb747e24'
    if _name == '삼성생명':
        return '4ff9fde083e595ee'


