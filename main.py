import os
import json
import shutil
from rich.console import Console
from rich.traceback import install

console = Console()
install()

class Converter():
    ''' ai-hub에서 받은 라벨링 데이터를 아래 코드에 따라 분리하고 yolo 형식으로 txt를 생성한다.
        \n이동식 비계 WO-03
        \n안전 발판 위 2명 이상 오르는 행위 UA-07, UA-13, UA-25
    '''
    SOURCE_INFO = 'Source Data Info.'
    ID = 'source_data_ID'
    EXETENSION = 'file_extension'
    LEARNING_INFO = 'Learning Data Info.'
    ANNOTATION = 'annotation'
    DIR_PATH = './'
    SAVE_PATH = './output/'
    IMAGE_PATH = './images/'

    def __init__(self):
        self.target_path = []
        self.class_id = []
        self.box = []
        self.name = []
        self.img_format = []
        print('경로 탐색 중...')
        for (root, directories, files) in os.walk(self.DIR_PATH):
            for file in files:
                if '.json' in file:
                    self.target_path.append(os.path.join(root, file))

    def open_file(self):
        print('파일 읽는 중...')
        for i in range(len(self.target_path)):
            with open(self.target_path[i], 'r', encoding='UTF-8') as f:
                json_data = json.load(f)
                source = json_data[self.SOURCE_INFO]
                name = source[self.ID]
                img_format = source[self.EXETENSION]
                self.name.append(name)
                self.img_format.append(f'.{img_format}') # .jpg
                annotation = json_data[self.LEARNING_INFO][self.ANNOTATION][0]
                self.class_id.append(annotation['class_id'])
                self.box.append(annotation['box'])
        print('파읽 읽기 성공')

    def save_file(self):
        for i in range(len(self.target_path)):
            save_path = self.SAVE_PATH + self.name[i] + '.txt'
            with open(save_path, 'w') as f: 
                data = str(self.box[i])[1:-1] # 1 576.6264683489982, 40.437736953175545, 872.9008530567477, 870.0684587565511
                f.write(f'1 {data}')
            # 이미지 복사하기
            img_path = self.IMAGE_PATH + self.name[i] + self.img_format[i]
            img_destination = self.SAVE_PATH + self.name[i] + self.img_format[i]
            shutil.copyfile(img_path, img_destination)

    def main(self):
        self.open_file()
        self.save_file()

if __name__ == '__main__':
    converter = Converter()
    converter.main()
