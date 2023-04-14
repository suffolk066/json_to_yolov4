import os
import json
import shutil
import pybboxes as pbx
from rich.console import Console
from rich.traceback import install

console = Console()
install()

class Converter:
    DATA_INFO = 'Raw Data Info.'
    RESOLUTION = 'resolution'
    SOURCE_INFO = 'Source Data Info.'
    ID = 'source_data_ID'
    EXTENSION = 'file_extension'
    LEARNING_INFO = 'Learning Data Info.'
    ANNOTATION = 'annotation'
    DIR_PATH = './'
    SAVE_PATH = './output/'
    IMAGE_PATH = './images/'
    FIND_NAME = 'UA-07'

    def __init__(self):
        self.resolution = ()
        self.target_paths = [
            os.path.join(root, file)
            for root, directories, files in os.walk(self.DIR_PATH)
            for file in files
            if '.json' in file
        ]

    def convert_yolo(self, annotations):
        class_ids = []
        boxes = []
        for annotation in annotations:
            class_name = annotation['class_id']
            if class_name == self.FIND_NAME:
                class_ids.append(class_name)
                bbox = tuple(annotation['box'])
                yolo_bbox = pbx.convert_bbox(bbox, from_type='coco', to_type='yolo', image_size=self.resolution)
                boxes.append(yolo_bbox)
        return class_ids, boxes

    def process_files(self):
        file_names = []
        img_formats = []
        class_ids = []
        boxes = []

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
                current_class_ids, current_boxes = self.convert_yolo(annotations)
                class_ids.extend(current_class_ids)
                boxes.extend(current_boxes)

        return file_names, img_formats, class_ids, boxes

    def save_files(self, file_names, img_formats, class_ids, boxes):
        with open(self.SAVE_PATH + 'classes.txt', 'w') as class_file:
            class_file.write(class_ids[0])

        for i, file_name in enumerate(file_names):
            save_path = f"{self.SAVE_PATH}{file_name}.txt"
            with open(save_path, 'w') as f:
                data = boxes[i]
                data_str = f"0 {data[0]} {data[1]} {data[2]} {data[3]}"
                f.write(data_str)

            img_path = f"{self.IMAGE_PATH}{file_name}{img_formats[i]}"
            img_destination = f"{self.SAVE_PATH}{file_name}{img_formats[i]}"
            shutil.copyfile(img_path, img_destination)

    def main(self):
        file_names, img_formats, class_ids, boxes = self.process_files()
        self.save_files(file_names, img_formats, class_ids, boxes)

if __name__ == '__main__':
    converter = Converter()
    converter.main()

