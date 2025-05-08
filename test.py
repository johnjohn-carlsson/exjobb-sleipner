import zipfile
import glob

wheel_path = glob.glob("./libs/packages/defusedxml-*.whl")[0]
with zipfile.ZipFile(wheel_path, 'r') as zip_ref:
    zip_ref.extractall("./libs/packages/defusedxml")