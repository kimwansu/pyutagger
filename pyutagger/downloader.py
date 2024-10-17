
import json
import os
import platform
import requests
import urllib
import zipfile

from tqdm import tqdm
from zlib import crc32
from hashlib import md5


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
        desc=os.path.split(local_fname)[-1],
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
    # 시스템 확인
    os_name = platform.system()
    if os_name == 'Windows':
        if user_install_path:
            install_path_base = user_install_path
        else:
            install_path_base = 'C:\\utagger\\'
        make_workdir(install_path_base)
        tmp_dir = os.path.join(install_path_base + 'tmp\\')
        make_workdir(tmp_dir)
        if ver == 'utagger4': # 유태거 4.0
            install_dir = os.path.join(install_path_base, 'v4_2403')
            url = 'http://203.250.77.242:8000/utg4demo_v2403.zip'
        elif ver == 'utagger4hj': # 유태거 4.0 훈민정음
            install_dir = os.path.join(install_path_base, 'hj_2403')
            url = 'http://203.250.77.242:8000/UTagger%ED%9B%88%EB%AF%BC%EC%A0%95%EC%9D%8C_TCM_2403.zip'
        elif ver == 'utagger3': # 유태거 3.0
            install_dir = os.path.join(install_path_base, 'v3_2109')
            url = 'http://203.250.77.242:8000/utagger%20delay%202021%2009%20centos7.8%20windown%20py%20jna%20v1.2.7z'
        else:
            return False
    else:
        return False
    
    # 다운로드
    pure_fname = urllib.parse.unquote(os.path.split(url)[-1])
    local_fname = os.path.join(tmp_dir, pure_fname)
    if os.path.exists(local_fname) and os.path.isfile(local_fname):
        os.remove(local_fname)
    download_file(url, local_fname)
    if os.path.exists(install_dir) and os.path.isdir(install_dir) and len(os.listdir(install_dir)) > 0:
        for i in range(1, 100):
            bak_dname = install_dir + f'_{i}'
            if os.path.exists(bak_dname) and os.path.isdir(bak_dname):
                continue
            else:
                os.rename(install_dir, bak_dname)
                print(f'기존 버전 설치 위치는 {bak_dname}으로 이름을 변경했습니다.')
                break
    
    unzip_file(local_fname, install_dir)
    
    generate_config_file(install_dir, ver)
    return True


def test():
    install_utagger('utagger3')


if __name__ == '__main__':
    test()
    