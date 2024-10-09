import json
import os
import platform
import sys
from ctypes import *

from pyutagger.hangul_util import *


def read_config():
    home_dir = os.path.expanduser('~')
    config_fname = 'pyutagger_path.json'
    config_path = os.path.join(home_dir, config_fname)
    if not os.path.exists(config_path) or not os.path.isfile(config_path):
        print('설정 파일 불러오기 실패.')
        print('Failed to load config file.')
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config

config = read_config()
if not config:
    sys.exit(1)
    

class UTagger:
    def __init__(self, tagger):
        self.tagger = tagger
        self.load_ = False
        
    def __version__(self):
        return '0.9.1.578'
    
    def load(self):
        self.tagger.load()
        self.load_ = True
    
    def release(self):
        self.tagger.release()
        self.load_ = False
    
    def tagger_name(self):
        return self.tagger.name
    
    def analyse(self, text):
        if not self.load_:
            return None
        
        tagged = self.tagger.tag(text)
        return tagged
    
    def morphs(self, text):
        if not self.load_:
            return None
        
        tagged = self.analyse(text)
        parsed = [BSP(*bsp) for bsp in parse_sent(tagged, flattern=True)]
        morphs = [bsp.B for bsp in parsed]
        return morphs
    
    def nouns(self, text):
        if not self.load_:
            return None
        
        tagged = self.analyse(text)
        parsed = [BSP(*bsp) for bsp in parse_sent(tagged, flattern=True)]
        return [bsp.B for bsp in parsed if bsp.P[:2] == 'NN']
        
    def pos(self, text):
        if not self.load_:
            return None
        
        tagged = self.analyse(text)
        parsed = [BSP(*bsp) for bsp in parse_sent(tagged, flattern=True)]
        return [(bsp.BS, bsp.P) for bsp in parsed]
    
        
    

class UTagger4:
    def __init__(self, utg4_path, name='UTagger 4', desc=''):
        self.name = name
        self.description = desc
        
        self.utg4_path = utg4_path
        os_name = platform.system()
        lib_ext = '.dll' if os_name == 'Windows' else '.so'
        self.utg4_lib_fname = 'bin\\LibUMA4' + lib_ext
        self.utg4_lib = None
        
    def load(self):
        lib_path = os.path.join(self.utg4_path, self.utg4_lib_fname)
        print('LIB: ', lib_path)
        try:
            bin_path = os.path.join(self.utg4_path, 'bin')
            print('BIN: ', bin_path)
            os.chdir(bin_path)
        except FileNotFoundError:
            print('dir not found')
        except PermissionError:
            print('permission error')
        self.utg4_lib = cdll.LoadLibrary(lib_path)
        self.utg4_lib.load_uma()
    
    def release(self):
        self.utg4_lib.release()
        self.utg4_lib = None
    
    def tag(self, text):
        if not self.utg4_lib:
            return 'ERROR: UTagger not loaded'
        
        surf = text.strip()
        surf_u8 = surf.encode('utf-8')
        c_surf = c_char_p(surf_u8)
        c_tagged = create_string_buffer(len(surf_u8) * 16)
        self.utg4_lib.tag_uma(c_surf, c_tagged)
        tagged = c_tagged.raw.decode('utf-8').strip('\0')
        tagged = tagged.strip()
        return tagged
    
    
class UTagger3:
    def __init__(self, utg3_path, name='UTagger 3', desc=''):
        self.name = name
        self.description = desc
        
        self.utg3_path = utg3_path
        
    
    def load(self):
        raise NotImplementedError
    
    def release(self):
        raise NotImplementedError

    def tag(self, text):
        raise NotImplementedError
    
    
def utagger_loader(ver):
    if ver == 'utagger4':
        tagger = UTagger(UTagger4(config[ver], desc='UTagger 4'))
    elif ver == 'utagger4hj':
        tagger = UTagger(UTagger4(config[ver], name='UTagger 4 훈민정음', desc='UTagger 4 훈민정음'))
    elif ver == 'utagger3':
        raise NotImplementedError
    else:
        return None
    
    return tagger


def test():
    print('설치된 유태거 목록: ', config)
    print()
    
    utg4 = utagger_loader('utagger4')
    if not utg4:
        print('로드 실패')
        print('failed to load')
        sys.exit(1)
        
    utg4.load()
    print(utg4.tagger_name)
    s = '대통령배생존대회에서 배가침몰하는중에도 배씨는배를먹으면서 배를채우고 배영하며 버티는데 나보다두배는더용감했다.'
    print('원문: ', s)
    tagged = utg4.analyse(s)
    print('형태소 분석: ', tagged)
    morphs = utg4.morphs(s)
    print('형태소 각각 분리: ', morphs)
    nouns = utg4.nouns(s)
    print('명사만: ', nouns)
    pos = utg4.pos(s)
    print('형태소 품사 각각', pos)
    
    utg4.release()
    print('Ok.')
    
    
    
if __name__ == '__main__':
    test()
    