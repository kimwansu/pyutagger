# pyutagger
UTagger python wrapper

## 1. 유태거 다운로드
```py
import pyutagger.downloader as ud
# 필요에 따라 아래 두 가지 중 필요한 것을 다운로드한다.
# 기본적으로 윈도우에서는 c:\utagger에 다운로드를 시도한다.
# 다른 드라이브 또는 디렉토리에 설치하려면 추가 인자로 절대 경로를 추가하면 된다.
# 그러면 지정한 경로 밑에서 다운로드와 압축 해제가 진행된다.
ud.install_utagger('utagger3')    # 유태거 3
ud.install_utagger('utagger4')    # 유태거 4
ud.install_utagger('utagger4hj')  # 유태거 4 훈민정음(옛한글 전용)
```

* 주의사항: 간혹 설치 직후에 환경설정이 잘 불러와지지 않아서 유태거가 불러와지지 않는 경우에는 파이썬 인터프리터를 종료 후 다시 실행하면 됩니다.

## 2. 유태거 사용
* `utagger.py`에 있는 `test()`에 기능 사용 예시를 넣었다.
* 유태거 훈민정음을 사용하려면 `utg4 = utagger_loader('utagger4')`에서  `utagger4`를 `utagger4hj`로 바꾸면 된다.
```py
import pyutagger.utagger as ut

def test():
    utg4 = ut.utagger_loader('utagger4')
    if not utg4:
        print('로드 실패')
        print('failed to load')
        sys.exit(1)
        
    utg4.load()
    print(utg4.tagger_name())
    s = '대통령배 생존 대회에서 배가 침몰하는 중에도 배씨는 배를 먹으면서 배를 채우고 배영하며 버티는데 나보다 두 배는 더 용감했다.'
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
```

출력은 아래와 같다.
```
UTagger 4
원문:  대통령배생존대회에서 배가침몰하는중에도 배씨는배를먹으면서 배를채우고 배영하며 버티는데 나보다두배는더용감했다.
형태소 분석:  대통령/NNG+배__05/NNG+생존/NNG+대회__02/NNG+에서/JKB 배__02/NNG+가/JKS+침몰하/VV+는/ETM+중__04/NNB+에/JKB+도/JX 배__10/NNP+씨__07/NNB+는/JX+배__01/NNG+를/JKO+먹__02/VV+으면서/EC 배__01/NNG+를/JKO+채우__03/VV+고/EC 배영하/NNP+ 며/EC 버티/VV+는데/EF 나__03/NP+보다/JKB+두__01/MMN+배__09/NNG+는/JX+더__01/MAG+용감하/VA+였/EP+다/EF+./SF
형태소 각각 분리:  ['대통령', '배', '생존', '대회', '에서', '배', '가', '침몰하', '는', '중', '에', '도', '배', '씨', ' 는', '배', '를', '먹', '으면서', '배', '를', '채우', '고', '배영하', '며', '버티', '는데', '나', '보다', '두', '배', '는', '더', '용감하', '였', '다', '.']
명사만:  ['대통령', '배', '생존', '대회', '배', '중', '배', '씨', '배', '배', '배영하', '배']
형태소 품사 각각 [('대통령', 'NNG'), ('배__05', 'NNG'), ('생존', 'NNG'), ('대회__02', 'NNG'), ('에서', 'JKB'), ('배__02', 'NNG'), ('가', 'JKS'), ('침몰하', 'VV'), ('는', 'ETM'), ('중__04', 'NNB'), ('에', 'JKB'), ('도', 'JX'), ('배__10', 'NNP'), ('씨__07', 'NNB'), ('는', 'JX'), ('배__01', 'NNG'), ('를', 'JKO'), ('먹__02', 'VV'), ('으면서', 'EC'), ('배__01', 'NNG'), ('를', 'JKO'), ('채우__03', 'VV'), ('고', 'EC'), ('배영하', 'NNP'), ('며', 'EC'), ('버티', 'VV'), ('는데', 'EF'), ('나__03', 'NP'), ('보다', 'JKB'), ('두__01', 'MMN'), ('배__09', 'NNG'), ('는', 'JX'), ('더__01', 'MAG'), ('용감하', 'VA'), ('였', 'EP'), ('다', 'EF'), ('.', 'SF')]
```
