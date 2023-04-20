import os
import json
import shutil
import pybboxes as pbx
from rich.console import Console
from rich.traceback import install

console = Console()
install()

class Converter:
    # 파일 경로
    DIR_PATH = './json/' # json 파일 넣는 곳
    IMAGE_PATH = './images/' # 이미지 넣는 곳
    SAVE_PATH = './output/' # 저장 경로

    # 해상도 추출용
    DATA_INFO = 'Raw Data Info.'
    RESOLUTION = 'resolution'

    # 파일명, 이미지 확장자 추출용
    SOURCE_INFO = 'Source Data Info.'
    ID = 'source_data_ID'
    EXTENSION = 'file_extension'

    # 바운딩박스 추출용
    LEARNING_INFO = 'Learning Data Info.'
    ANNOTATION = 'annotation'

    def __init__(self):
        self.id_list = {'WO-01' : 'worker',
            'WO-02' : 'worker',
            'WO-03' : 'scaffold',
            'SO-02' : 'workplate'}
        self.resolution = ()

        # json 파일을 읽고 파일 이름을 저장한다.
        self.target_paths = [
            os.path.join(root, file)
            for root, directories, files in os.walk(self.DIR_PATH)
            for file in files
            if '.json' in file
        ]

    # 바운딩박스 COCO to YOLO 변환
    def convert_yolo(self, annotations):
        data_list = []

        for annotation in annotations:
            class_id = annotation['class_id']
            bbox = tuple(annotation['box'])
            yolo_bbox = pbx.convert_bbox(bbox, from_type='coco', to_type='yolo', image_size=self.resolution)

            data_dict = {
                'class_id': class_id,
                'bbox': yolo_bbox
            }
            data_list.append(data_dict)
        return data_list

    def process_files(self):
        file_names = []
        img_formats = []
        data_dicts = []

        # for target_path in self.target_paths:
        for target_path in self.target_paths:
            with open(target_path, 'r', encoding='UTF-8') as f:
                json_data = json.load(f)
                self.resolution = tuple(json_data[self.DATA_INFO][self.RESOLUTION])

                source = json_data[self.SOURCE_INFO]
                file_name = source[self.ID]
                img_format = f".{source[self.EXTENSION]}"
                file_names.append(file_name)
                img_formats.append(img_format)

                annotations = json_data[self.LEARNING_INFO][self.ANNOTATION]
                current_data_list = self.convert_yolo(annotations)
                data_dicts.append(current_data_list)
        return file_names, img_formats, data_dicts

    def save_files(self, file_names, img_formats, data_dicts):
        # 클래스 이름 중복 제거 및 총갯수 구하기
        unique_class_ids = set()
        for data_dict in data_dicts:
            for class_dict in data_dict:
                unique_class_ids.add(class_dict['class_id'])

        # 클래스 이름을 classes.txt로 저장
        with open(self.SAVE_PATH + 'classes.txt', 'w') as class_file:
            for class_id in unique_class_ids:
                class_file.write(f"{class_id}\n")

        # 각 이미지에 대한 바운딩 박스 정보를 저장
        for i, file_name in enumerate(file_names):
            save_path = f"{self.SAVE_PATH}{file_name}.txt"
            with open(save_path, 'w') as f:
                for class_dict in data_dicts[i]:
                    class_id = class_dict['class_id']
                    bbox = class_dict['bbox']
                    class_index = list(unique_class_ids).index(class_id)
                    data_str = f"{class_index} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n"
                    f.write(data_str)

            # 이미지 파일을 복사
            img_path = self.IMAGE_PATH + file_name + img_formats[i] # ./images/H-210726_A04_A_WS-04_201_0016.jpg
            img_destination = self.SAVE_PATH + file_name + img_formats[i] # ./output/H-210726_A04_A_WS-04_201_0016.jpg
            shutil.copyfile(img_path, img_destination) # ./images에서 ./output으로 파일 복사

    def main(self):
        file_names, img_formats, data_dicts = self.process_files()
        self.save_files(file_names, img_formats, data_dicts)

if __name__ == '__main__':
    converter = Converter()
    converter.main()