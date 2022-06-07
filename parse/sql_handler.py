from util.struct import MusicData, AkaData

# QUERY FIELD
INIT_QUERY_MASTER = '''SELECT count(*) FROM sqlite_master WHERE type= "table" AND name = "METADATA";'''
QUERY_METADATA = '''SELECT * FROM METADATA;'''
QUERY_MUSIC = '''SELECT * FROM MUSIC;'''
QUERY_AKA = '''SELECT * FROM AKA;'''
QUERY_MEME = '''SELECT * FROM MEME;'''

# DROP THEM ALL!
DROP_METADATA = '''DROP TABLE IF EXISTS METADATA;'''
DROP_MUSIC = '''DROP TABLE IF EXISTS MUSIC;'''
DROP_AKA = '''DROP TABLE IF EXISTS AKA;'''
DROP_MEME = '''DROP TABLE IF EXISTS MEME;'''

# CREATE TABLES
CREATE_MUSIC = '''
    CREATE TABLE MUSIC(

    MID INT PRIMARY KEY NOT NULL ,
    NAME VARCHAR NOT NULL ,
    NAME_YO VARCHAR NOT NULL ,
    ARTIST VARCHAR NOT NULL ,
    ARTIST_YO VARCHAR NOT NULL ,
    MUSIC_ASCII VARCHAR NOT NULL ,
    BPM_MAX INT NOT NULL ,
    BPM_MIN INT NOT NULL ,
    DATE INT NOT NULL ,
    VERSION INT NOT NULL ,
    INF_VER INT ,

    NOV_LV INT ,
    NOV_ILL VARCHAR ,
    NOV_EFF VARCHAR ,
    NOV_NTS INT ,
    NOV_PEK INT ,
    NOV_TMM INT ,
    NOV_TRK INT ,
    NOV_HDT INT ,
    NOV_OHD INT ,
    
    ADV_LV INT ,
    ADV_ILL VARCHAR ,
    ADV_EFF VARCHAR ,
    ADV_NTS INT ,
    ADV_PEK INT ,
    ADV_TMM INT ,
    ADV_TRK INT ,
    ADV_HDT INT ,
    ADV_OHD INT ,
    
    EXH_LV INT ,
    EXH_ILL VARCHAR ,
    EXH_EFF VARCHAR ,
    EXH_NTS INT ,
    EXH_PEK INT ,
    EXH_TMM INT ,
    EXH_TRK INT ,
    EXH_HDT INT ,
    EXH_OHD INT ,
    
    INF_LV INT ,
    INF_ILL VARCHAR ,
    INF_EFF VARCHAR ,
    INF_NTS INT ,
    INF_PEK INT ,
    INF_TMM INT ,
    INF_TRK INT ,
    INF_HDT INT ,
    INF_OHD INT ,
    
    MXM_LV INT ,
    MXM_ILL VARCHAR ,
    MXM_EFF VARCHAR ,
    MXM_NTS INT ,
    MXM_PEK INT ,
    MXM_TMM INT ,
    MXM_TRK INT ,
    MXM_HDT INT ,
    MXM_OHD INT ,);'''
CREATE_AKA = '''CREATE TABLE AKA (AID INT PRIMARY KEY NOT NULL, NAME VARCHAR);'''
CREATE_MEME = '''CREATE TABLE SEARCH (MID INT PRIMARY KEY NOT NULL, MEME_STR VARCHAR);'''


# INSERT TABLES
def CREATE_AND_INSERT_METADATA(meta_version: int, contents: dict) -> tuple:
    if meta_version == 1:
        return _METADATA_V1(contents)
    else:
        raise RuntimeError('Unsupported metadata version.')


def _METADATA_V1(contents: dict) -> tuple:
    """
    Version 1 of METADATA has 4 rows, namely
    METADATA_VER: version of metadata, fixed on 1
    FIX_VER     : an optional version code of metadata, allows developer to upgrade database without changing other
                  version code
    SDVX_VER    : version of game itself, drew from ea3-config.xml
    MAP_SIZE    : maximum mid of all musics
    """
    CREATE_METADATA = '''
        CREATE TABLE METADATA(
        METADATA_VER INT PRIMARY KEY NOT NULL ,
        SDVX_VER INT NOT NULL ,
        MAP_SIZE INT NOT NULL);'''
    INSERT_METADATA = '''
        INSERT INTO METADATA (METADATA_VER, FIX_VER, SDVX_VER, MAP_SIZE) 
        VALUES (1, %d, %d, %d);
        ''' % (contents['FIX_VER'], contents['SDVX_VER'], contents['MAP_SIZE'])

    return CREATE_METADATA, INSERT_METADATA


def INSERT_MUSIC(md: MusicData) -> str:
    res = ['INSERT INTO MUSIC ('
           'MID, NAME, NAME_YO, ARTIST, ARTIST_YO, MUSIC_ASCII, '
           'BPM_MAX, BPM_MIN, DATE, VERSION, INF_VER, '
           'NOV_LV, NOV_ILL, NOV_EFF, NOV_NTS, NOV_PEK, NOV_TMM, NOV_TRK, NOV_HDT, NOV_OHD,'
           'ADV_LV, ADV_ILL, ADV_EFF, ADV_NTS, ADV_PEK, ADV_TMM, ADV_TRK, ADV_HDT, ADV_OHD,'
           'EXH_LV, EXH_ILL, EXH_EFF, EXH_NTS, EXH_PEK, EXH_TMM, EXH_TRK, EXH_HDT, EXH_OHD,'
           'INF_LV, INF_ILL, INF_EFF, INF_NTS, INF_PEK, INF_TMM, INF_TRK, INF_HDT, INF_OHD,'
           'MXM_LV, MXM_ILL, MXM_EFF, MXM_NTS, MXM_PEK, MXM_TMM, MXM_TRK, MXM_HDT, MXM_OHD,) VALUES (']

    common_data = [md.mID, md.name, md.nameYmgn, md.artist, md.artistYmgn, md.ascii,
                   md.bpmMax, md.bpmMin, md.date, md.version, md.infVer]
    diffs = [md.novice, md.advanced, md.exhausted, md.infinite, md.maximum]

    for data in common_data:
        res.append(_get_sql_str(data))
    for diff in diffs:
        diff_data = [diff.level, diff.illustrator, diff.effector,
                     diff.notes, diff.peak, diff.tsumami, diff.tricky, diff.handTrip, diff.oneHand]
        res.append(_get_sql_str(diff_data))

    res.append(');')
    return ''.join(res)

def INSERT_AKA(ad: AkaData) -> str:
    pass


def _get_sql_str(variable: int or str) -> str:
    if isinstance(variable, int):
        return str(variable)
    elif isinstance(variable, str):
        return '\'%s\'' % variable.replace('\'', '\'\'')
