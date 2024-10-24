
import json
import os
import platform
import requests
import urllib
import zipfile

from tqdm import tqdm
from hashlib import sha1


def make_workdir(workdir):
    if not workdir:
        return False
    
    if not os.path.exists(workdir):
        # 윈도우, 리눅스 양쪽 모두 디렉토리를 만들 위치에 해당하는 상위 디렉토리는 항상 존재한다.
        os.mkdir(workdir)

    # 제대로 만들어졌는지 검사한다.
    if os.path.exists(workdir) and os.path.isdir(workdir):
        return True
    else:
        return False
    
    
def download_file(url, local_fname):
    try:
        res = requests.get(url, stream=True)
    except:
        print('다운로드 실패')
        return False
    
    fsize_in_bytes = int(res.headers.get('content-length', 0))
    block_size = 32768
    
    with open(local_fname, 'wb') as f, tqdm(
        desc=f'DOWNLOAD {os.path.split(local_fname)[-1]}',
        total=fsize_in_bytes,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024
    ) as bar:
        for chunk in res.iter_content(chunk_size=block_size):
            bar.update(len(chunk))
            f.write(chunk)
    
    print(f'Download  [ok]')
    return True


def hash_file(local_fname, fsize=0, bufsize=32768, hash_func=sha1):
    hasher = hash_func()
    fsize_in_bytes = fsize if fsize else os.path.getsize(local_fname)
    with open(local_fname, 'rb') as f, tqdm(
        desc=f'HASH {os.path.split(local_fname)[-1]}',
        total=fsize_in_bytes,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024
    ) as bar:
        buf = f.read(bufsize)
        bar.update(f.tell())
        while buf:
            hasher.update(buf)
            buf = f.read(bufsize)
            bar.update(f.tell())
    return hasher.hexdigest()


def unzip_file(zip_fname, target_path):
    with zipfile.ZipFile(zip_fname, 'r') as zf:
        file_list = zf.infolist()
        total_size = sum(file.file_size for file in file_list)
        
        with tqdm(total=total_size, unit='B', unit_scale=True, desc='Extracting: ') as pbar:
            for file in file_list:
                zf.extract(file, target_path)
                pbar.update(file.file_size)
                
    return True


def generate_config_file(utagger_path, ver):
    home_dir = os.path.expanduser('~')
    config_fname = 'pyutagger_path.json'
    config_path = os.path.join(home_dir, config_fname)
    config = dict()
    # 이미 설정 파일이 존재하고 있으면 그 내용을 불러온다.
    if os.path.exists(config_path) and os.path.isfile(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    utagger_path = utagger_path.strip()
    config[ver] = utagger_path
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def install_utagger(ver='utagger4', user_install_path=''):
    # 최초 설치 또는 프로그램 버전 업데이트에만 사용한다.
    # 학습 사전만을 업데이트하는 경우에는 update_utagger_data를 사용한다.
    
    # 시스템 확인
    os_name = platform.system()
    if user_install_path:
        install_path_base = user_install_path
    elif os_name == 'Windows':
        install_path_base = 'C:\\utagger\\'
    elif os_name == 'Linux':
        home_dir = os.path.expanduser('~')
        install_path_base = os.path.join(home_dir, 'utagger')
    else:
        print('지원하지 않는 운영체제')
        return False
    
    make_workdir(install_path_base)
    tmp_dir = os.path.join(install_path_base + 'tmp')
    make_workdir(tmp_dir)
    
    utagger_dir_url = "http://203.250.77.242:8000/utagger_dir.json"
    try:
        res = requests.get(utagger_dir_url)
        if res.status_code != 200:
            print('유태거 파일 위치를 찾을 수 없습니다.')
            return False
        utagger_directory = json.loads(res.content.decode('utf-8'))
    except:
        print("파일 목록 조회 실패")
        return False
    
    if f'{ver}-bin' not in utagger_directory:
        print('존재하지 않는 버전: ', ver)
        return False
    
    # 최신 버전명을 설치 디렉토리로 한다.
    target_dir = utagger_directory[f'{ver}-bin']['lastest']  # 최신 버전의 버전 번호
    install_dir = os.path.join(install_path_base, target_dir)
    
    if os.path.exists(install_dir) and os.path.isdir(install_dir) and len(os.listdir(install_dir)) > 0:
        for i in range(1, 100):
            bak_dname = install_dir + f'_{i}'
            if os.path.exists(bak_dname) and os.path.isdir(bak_dname):
                continue
            else:
                os.rename(install_dir, bak_dname)
                print(f'기존 버전 설치 위치는 {bak_dname}으로 이름을 변경했습니다.')
                break
    
    for tgt in ['bin', 'data']:
        target_repo = utagger_directory[f'{ver}-{tgt}']['lastest']
        url = utagger_directory[f'{ver}-{tgt}'][target_repo]['url']
        
        # 다운로드
        pure_fname = urllib.parse.unquote(os.path.split(url)[-1])
        local_fname = os.path.join(tmp_dir, pure_fname)
        same_file_exists = False
        if os.path.exists(local_fname) and os.path.isfile(local_fname):
            ori_fsize = utagger_directory[ver][target_dir]['size']
            local_fsize = os.path.getsize(local_fname)
            if ori_fsize == local_fsize:
                ori_hash = utagger_directory[ver][target_dir]['hash']
                local_hash = hash_file(local_fname, fsize=local_fsize)
                if ori_hash == local_hash:
                    same_file_exists = True
            
            if not same_file_exists:
                os.remove(local_fname)

        if not same_file_exists:
            download_file(url, local_fname)
        
        unzip_file(local_fname, install_dir)
    
    generate_config_file(install_dir, ver)
    return True


def update_utagger_data(ver='utagger4'):
    # 현재 사용하는 버전의 유태거의 학습사전의 새 버전이 있으면 받는다.
    
    home_dir = os.path.expanduser('~')
    config_fname = 'pyutagger_path.json'
    config_path = os.path.join(home_dir, config_fname)
    config = dict()
    # 이미 설정 파일이 존재하고 있으면 그 내용을 불러온다.
    if os.path.exists(config_path) and os.path.isfile(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        print('유태거가 설치된 위치를 찾을 수 없습니다. 설정 파일을 점검해야 합니다.')
        return False
    
    
    utagger_dir_url = "http://203.250.77.242:8000/utagger_dir.json"
    try:
        res = requests.get(utagger_dir_url)
        if res.status_code != 200:
            print('유태거 파일 위치를 찾을 수 없습니다.')
            return False
        utagger_directory = json.loads(res.content.decode('utf-8'))
    except:
        print("파일 목록 조회 실패")
        return False
    
    if f'{ver}-data' not in utagger_directory:
        print('존재하지 않는 버전: ', ver)
        return False
    
    # 기존 설정파일 백업
    utagger_path_dir = config[ver]
    if '3' in ver:
        # 유태거3은 hlxcfg.txt 파일을 백업한다.
        utg_bin_config_fname = os.path.join(utagger_path_dir, 'Hlxcfg.txt')
        bak_config_fname = utg_bin_config_fname + '.bak'
        
        # 기존 유태거 설정파일에서 마지막으로 사용된 학습사전 폴더를 특정한다.
        with open(utg_bin_config_fname, 'r', encoding='utf-8') as f:
            config_lines = [l.rstrip() for l in f.readlines()]
            data_path = ''
            for line in config_lines:
                if line[:8] == 'HLX_DIR ':
                    tokens = [t for t in line.split('/') if len(t) > 0]
                    data_path = os.path.join(utagger_path_dir, tokens[-1])
                    break
            if not data_path:
                print('설정 파일에서 학습사전이 있는 폴더를 찾을 수 없습니다.')
                return False

        cuscor_fname = os.path.join(data_path, 'customDic.txt')
        bak_cuscor_fname = os.path.join(utagger_path_dir, 'customDict.txt.bak')
        
    elif '4' in ver:
        # 유태거4(훈민정음 포함)는 MFL_data/MFL_data_UMA4/config.txt 파일을 백업한다.
        utg_bin_config_fname = os.path.join(utagger_path_dir, 'MFL_data/MFL_data_UMA4/config.txt')
        bak_config_fname = os.path.join(utagger_path_dir, f'config.txt.bak')
        data_path = os.path.join(utagger_path_dir, 'MFL_data')
        cuscor_fname = os.path.join(data_path, 'cus cor.tag')
        bak_cuscor_fname = os.path.join(utagger_path_dir, 'cus cor.tag.bak')

    else:
        print('잘못된 버전 지정: ', ver)
        return False
    
        
    if os.path.exists(bak_config_fname):
        for i in range(1, 100):
            alt_bak_config_fname = bak_config_fname[:-4] + f'_{i}.bak'
            if not os.path.exists(alt_bak_config_fname):
                bak_config_fname = alt_bak_config_fname
                print(f'기존 설정 파일은 {bak_config_fname}으로 백업했습니다.')
                break
 
    os.rename(utg_bin_config_fname, bak_config_fname)
    
    if os.path.exists(bak_cuscor_fname):
        for i in range(1, 100):
            alt_bak_cuscor_fname = bak_cuscor_fname[:-4] + f'_{i}.bak'
            if not os.path.exists(alt_bak_cuscor_fname):
                bak_cuscor_fname = alt_bak_cuscor_fname
                print(f'기존 사용자 말뭉치 파일은 {bak_cuscor_fname}으로 백업했습니다.')
                break
    
    os.rename(cuscor_fname, bak_cuscor_fname)
        
    
    url = utagger_directory[f'{ver}-data']['url']
    # 설정파일에는 경로의 마지막에 디렉토리 구분자가 없다.
    tmp_dir = os.path.join(os.path.split(utagger_path_dir)[0], "tmp")
    target_dir = utagger_path_dir

    # 다운로드
    pure_fname = urllib.parse.unquote(os.path.split(url)[-1])
    local_fname = os.path.join(tmp_dir, pure_fname)
    same_file_exists = False
    if os.path.exists(local_fname) and os.path.isfile(local_fname):
        ori_fsize = utagger_directory[ver][target_dir]['size']
        local_fsize = os.path.getsize(local_fname)
        if ori_fsize == local_fsize:
            ori_hash = utagger_directory[ver][target_dir]['hash']
            local_hash = hash_file(local_fname, fsize=local_fsize)
            if ori_hash == local_hash:
                same_file_exists = True
        
        if not same_file_exists:
            os.remove(local_fname)

    if not same_file_exists:
        download_file(url, local_fname)
        
    # 설치 전 기존 학습사전이 있는 디렉토리를 제거한다
    if os.path.exists(data_path):
        os.remove(data_path)
    
    install_dir = utagger_path_dir
    unzip_file(local_fname, install_dir)
    
    return True


def test():
    install_utagger('utagger4')


if __name__ == '__main__':
    test()
    