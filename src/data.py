from zipfile import ZipFile
from pathlib import Path
import splitfolders
import argparse
import shutil
import cv2
import os


class Data:
    def __init__(self, env: str = "local"):
        if env == "local":
            self.project_root_path = str(Path().absolute())
        elif env == "colab":
            self.project_root_path = os.path.join(
                str(Path().absolute()), "cnn_leucemia"
            )
        else:
            raise Exception(f"ENV {env} invalid!")

    def unzip(self, colab: bool = False):
        """Extrai o data.zip no raiz do projeto"""
        print("Unzipping")
        if colab:
            data_zip_path = os.path.join(
                self.project_root_path, "cnn_leucemia", "data.zip"
            )
        else:
            data_zip_path = os.path.join(self.project_root_path, "data.zip")
        with ZipFile(data_zip_path, "r") as zipObj:
            unzip_path = os.path.join(self.project_root_path, "data")
            zipObj.extractall(unzip_path)
        print(f"File is unzipped in {unzip_path}")

    def split_data(
        self,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
    ):
        """split data/* into data/train/data, data/val/data, data/test/data

        Args:
            train_ratio (float, optional): Defaults to 0.7.
            val_ratio (float, optional): Defaults to 0.15.
            test_ratio (float, optional): Defaults to 0.15.
        """
        print(
            f"Spliting data into: train_ratio: {train_ratio} val_ratio: {val_ratio} test_ratio: {test_ratio}"
        )
        output_data_path = os.path.join(self.project_root_path, "output")
        intput_data_path = os.path.join(self.project_root_path, "data")
        splitfolders.ratio(
            input=intput_data_path,
            output=output_data_path,
            seed=42,
            ratio=(train_ratio, val_ratio, test_ratio),
            group_prefix=None,
        )

    def move_data_files(self):
        """Split folder creates a subfolder 'data' inside every folder
        this moves every image to data parent /train, /val, /test folder
        """
        print("Moving images to train, val and test folder")
        for folder in os.listdir(os.path.join(self.project_root_path, "output")):
            folder_path = os.path.join(self.project_root_path, "output", folder)
            print("------------------")
            print(folder_path)
            for sub_folder in os.listdir(folder_path):
                sub_folder_path = os.path.join(folder_path, sub_folder)
                print(sub_folder_path)
                for file in os.listdir(sub_folder_path):
                    file_path = os.path.join(sub_folder_path, file)
                    new_file_path = os.path.join(folder_path, file)
                    shutil.move(str(file_path), str(folder_path))

    def remove_subfolder_data(self):
        """Remove data/../data created on splitfolder"""
        print("Removing data subfolder")
        for folder in os.listdir(os.path.join(self.project_root_path, "output")):
            folder_path = os.path.join(self.project_root_path, "output", folder, "data")
            print(f"Removing {folder_path} folder")
            shutil.rmtree(str(folder_path))

    def create_class_folder(self):
        """Create class_a and class_b folder based on filename
        {...}0.jpeg = class_a
        {...}1.jpeg = class_b
        """
        print("Create class folder")
        for folder in os.listdir(os.path.join(self.project_root_path, "output")):
            folder_path = os.path.join(self.project_root_path, "output", folder)
            print("------------------")
            print(folder_path)
            class_a_path = os.path.join(folder_path, "class_a")
            class_b_path = os.path.join(folder_path, "class_b")
            try:
                os.mkdir(class_a_path)
            except OSError:
                print(f"Creation of the directory {class_a_path} failed")
            else:
                print(f"Successfully created the directory {class_a_path}")

            try:
                os.mkdir(class_b_path)
            except OSError:
                print(f"Creation of the directory {class_b_path} failed")
            else:
                print(f"Successfully created the directory {class_b_path} ")

            for file in os.listdir(folder_path):
                if file not in ["class_a", "class_b"]:
                    file_path = os.path.join(folder_path, file)
                    if "0.jpg" in file_path:
                        new_file_path = os.path.join(folder_path, "class_a", file)
                        shutil.move(str(file_path), str(new_file_path))
                    else:
                        new_file_path = os.path.join(folder_path, "class_b", file)
                        shutil.move(str(file_path), str(new_file_path))

    def rename_data_folder(self):
        """Delete data folder and rename output to data"""
        print("Renaming data folder")
        shutil.rmtree(os.path.join(self.project_root_path, "data"))
        os.rename(
            os.path.join(self.project_root_path, "output"),
            os.path.join(self.project_root_path, "data"),
        )

    def pre_process_images(self):
        print("Pre-processing images")
        for folder in os.listdir(os.path.join(self.project_root_path, "data")):
            folder_path = os.path.join(self.project_root_path, "data", folder)
            print(f"Pre-processing {folder_path}")
            for classe in os.listdir(folder_path):
                class_path = os.path.join(
                    self.project_root_path, "data", folder, classe
                )
                for file in os.listdir(class_path):
                    w_crop = 30  # pixel
                    y_crop = 30  # pixel

                    file_path = os.path.join(
                        self.project_root_path, "data", folder, classe, file
                    )
                    original_img = cv2.imread(file_path)
                    proc_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
                    _, proc_img = cv2.threshold(proc_img, 125, 300, cv2.THRESH_BINARY)

                    h = proc_img.shape[0]
                    w = proc_img.shape[1]
                    zoom_img = proc_img[y_crop : y_crop + h, w_crop : w_crop + w]

                    cv2.imwrite(file_path, zoom_img)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Configuracaoes para extracao das imagens"
    )

    parser.add_argument("enviroment", default="local", help="local or colab")

    args = parser.parse_args()

    data = Data(args.enviroment)
    data.unzip()
    data.split_data()
    data.move_data_files()
    data.remove_subfolder_data()
    data.create_class_folder()
    data.rename_data_folder()
    data.pre_process_images()
