"""
WHY USING THIS SHITTING CODING
"""


def amend_jis(jis_str: str) -> str:
    if not jis_str:
        return ''
    new = jis_str
    # latin field
    new = new \
        .replace("驫", "ā").replace("騫", "á").replace("曦", "à").replace('頽', 'ä').replace("罇", "ê") \
        .replace("曩", "è").replace("齷", "é").replace("彜", "ū").replace('骭', 'ü').replace("鬥", "Ã") \
        .replace("雋", "Ǜ").replace("隍", "Ü").replace("趁", "Ǣ").replace("鬆", "Ý").replace("驩", "Ø")
    # symbol field
    new = new \
        .replace("龕", "€").replace("蹇", "₂").replace("鬻", "♃").replace('黻', '*').replace('鑷', 'ゔ')
    # graph field
    new = new \
        .replace("齶", "♡").replace("齲", "❤").replace("躔", "★").replace('釁', '🍄').replace('齪', '♣') \
        .replace('鑈', '♦').replace('霻', '♠').replace('盥', '⚙')
    return new
