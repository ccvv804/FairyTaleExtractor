import zlib 
import os
import sys
import re
'''
동화나라 침공 계획
동화나라 추출기
5판 2021년 04월 30일
'''    
def 메인프로그램(파일경로):
    오픈파일=open(파일경로,'rb')
    읽은데이터=오픈파일.read()
    오픈파일.close()
    #현재폴더위치=os.getcwd()
    신파일이름 = os.path.splitext(os.path.basename(파일경로))[0]
    try:
        os.mkdir(신파일이름)
    except FileExistsError:
        print('폴더가 이미 있습니다! 프로그램이 잘못 작동될 가능성이 있습니다!') 
    os.chdir(신파일이름)
    이름위치=int.from_bytes(읽은데이터[20:24], byteorder='little') 
    고정이름위치=이름위치
    이름헤더=읽은데이터[이름위치:이름위치+12]
    인포이름헤더=이름헤더[0:4]
    압축푼이름크기=이름헤더[4:8]
    압축이름크기=이름헤더[8:12]
    압축이름크기숫자=int.from_bytes(압축이름크기, byteorder='little')
    이름카운터=0
    브레이크=False
    while True: 
        이름파일크기=읽은데이터[이름위치+12:이름위치+16]
        if 이름파일크기 == b'':
            break
        이름파일크기숫자=int.from_bytes(이름파일크기, byteorder='little')
        이름파일데이터=읽은데이터[이름위치+16:이름위치+16+이름파일크기숫자]
        압축풀린이름데이터=zlib.decompress(이름파일데이터)
        드디어이름이나왔다=re.sub(b'\x00', b'', 압축풀린이름데이터[:1024]).decode('EUC-KR', "replace")
        #print(드디어이름이나왔다)
        뉴파일주소=int.from_bytes(압축풀린이름데이터[1044:1048], byteorder='little')
        파일헤더=읽은데이터[뉴파일주소:20+뉴파일주소]
        인포파일헤더=파일헤더[0:4]
        압축푼파일크기=파일헤더[4:8]
        압축파일크기=파일헤더[8:12]
        모르는뒤헤더1=파일헤더[12:16]
        압축여부=파일헤더[16:20]
        압축파일크기숫자=int.from_bytes(압축파일크기, byteorder='little')
        파일데이터=읽은데이터[20+뉴파일주소:20+뉴파일주소+압축파일크기숫자] 
        if 압축여부 == b'\x00\x00\x00\x00':
            압축풀린데이터=파일데이터
        elif 압축여부 == b'\x01\x00\x00\x00': 
            압축풀린데이터=zlib.decompress(파일데이터)
        elif 압축여부 == b'\x02\x00\x00\x00': 
            print(드디어이름이나왔다+'는 암호화된 데이터입니다')
            압축풀린데이터=파일데이터
            브레이크=True
        elif 압축여부 == b'\x03\x00\x00\x00':
            print(드디어이름이나왔다+'는 압축 암호화된 데이터입니다')
            압축풀린데이터=zlib.decompress(파일데이터)
            브레이크=True
        else :
            print(드디어이름이나왔다+'는 미확인 타입 데이터입니다')
            압축풀린데이터=파일데이터
            print(압축여부)
            print(드디어이름이나왔다)
            브레이크=True
        기존압축풀린데이터=압축풀린데이터
        반복크기보정=0
        if 뉴파일주소+20+압축파일크기숫자 < 이름위치 and not 브레이크 :
            while True:
                #print(뉴파일주소+20+압축파일크기숫자+반복크기보정)
                다음파일헤더=읽은데이터[뉴파일주소+20+압축파일크기숫자+반복크기보정:뉴파일주소+40+압축파일크기숫자+반복크기보정]
                #print(다음파일헤더)
                다음인포파일헤더=다음파일헤더[0:4]
                다음압축푼파일크기=다음파일헤더[4:8]
                다음압축파일크기=다음파일헤더[8:12]
                다음압축파일크기숫자=int.from_bytes(다음압축파일크기, byteorder='little')
                다음모르는뒤헤더1=다음파일헤더[12:16]
                다음압축여부=다음파일헤더[16:20]
                if 다음인포파일헤더 == b'\x00\x00\x00\x00' :
                    break
                else:
                    뉴파일데이터=읽은데이터[뉴파일주소+40+압축파일크기숫자+반복크기보정:뉴파일주소+40+압축파일크기숫자+다음압축파일크기숫자+반복크기보정]
                    if 다음압축여부 == b'\x00\x00\x00\x00':
                        뉴압축풀린데이터=뉴파일데이터
                    elif 다음압축여부 == b'\x01\x00\x00\x00': 
                        뉴압축풀린데이터=zlib.decompress(뉴파일데이터)
                    else :
                        print('해독할 수 없는 타입입니다?')
                        뉴압축풀린데이터=뉴파일데이터
                        print(압축여부)
                    기존압축풀린데이터=기존압축풀린데이터+뉴압축풀린데이터
                    반복크기보정=반복크기보정+다음압축파일크기숫자+20
                    #print(반복크기보정)
        if not 브레이크:
            파일없는경로=os.path.split(드디어이름이나왔다)[0]
            if not 파일없는경로 == '':
                os.makedirs(파일없는경로, exist_ok=True)

            파일저장=open(드디어이름이나왔다,'bw')
            파일저장.write(기존압축풀린데이터)
            파일저장.close
        else :
            브레이크=False
        '''
        파일저장=open(str(이름카운터)+'.name','bw')
        파일저장.write(압축풀린이름데이터)
        파일저장.close
        '''
        이름위치=이름위치+4+이름파일크기숫자
        이름카운터=이름카운터+1
    #os.chdir(현재폴더위치)

print('동화나라 추출기 5판')
print('2021년 04월 30일')
입력받은파일경로 = sys.argv[1]
메인프로그램(입력받은파일경로)

'''
def search(dirname):    
    for (path, dir, files) in os.walk(dirname):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.pkg':
                메인프로그램(path+"/"+filename)     
            elif ext == '.PKG':
                메인프로그램(path+"/"+filename)  
search("./in")
'''