import base64


def decode_b64(msg: str, dst: str):
    _f = open(dst, 'wb')
    _f.write(base64.b64decode(msg))
    _f.close()


def jis_2_utf(jis: str, utf: str):
    jis_xml = open(jis, 'r', encoding='cp932')
    jis_data = jis_xml.readlines()
    jis_xml.close()

    utf_xml = open(utf, 'w', encoding='utf-8')
    utf_xml.write('<?xml version="1.0" encoding="utf-8"?>\n')
    jis_data.pop(0)
    for line in jis_data:
        utf_xml.write(line)
    utf_xml.close()


def amend_jis(jis_str: str) -> str:
    if not jis_str:
        return ''
    new = jis_str
    # latin field
    new = new\
        .replace("驫", "ā").replace("騫", "á").replace("曦", "à").replace('頽', 'ä').replace("罇", "ê").replace("曩", "è")\
        .replace("齷", "é").replace("彜", "ū").replace("鬥", "Ã").replace("雋", "Ǜ").replace("隍", "Ü").replace("趁", "Ǣ")\
        .replace("鬆", "Ý").replace("驩", "Ø")
    # symbol field
    new = new\
        .replace("龕", "€").replace("蹇", "₂").replace("鬻", "♃").replace('黻', '*')
    # graph field
    new = new\
        .replace("齶", "♡").replace("齲", "❤").replace("躔", "★").replace('釁', '🍄').replace('齪', '♣').replace('鑈', '♦')\
        .replace('霻', '♠')
    return new
