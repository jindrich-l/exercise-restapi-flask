import os
from flask import Flask, json, jsonify, request, make_response
from flask_cors import CORS
from stat import *
from typing import NamedTuple
from datetime import datetime

# load application config
CONFIG_FILE = "./config.json"
with open(CONFIG_FILE, "r") as fp:
    conf = json.load(fp)

try:
    BASEDIR = os.path.abspath(os.path.realpath(os.path.normpath(conf["api_root"])))
except:
    ValueError('"api_root" is not defined in config.json')

app = Flask(__name__)

# enable requests to this api from all origins (different ip adress/port}
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

class FileMeta(NamedTuple):
    filename: str
    is_folder: bool
    size: int
    creation_date: datetime
    modified_date: datetime
    mode: str


def map_stat_to_meta(filepath, stat):
    return FileMeta(filename=os.path.basename(filepath[len(BASEDIR):]),
                    is_folder=S_ISDIR(stat.st_mode),
                    size=stat.st_size,
                    creation_date=datetime.utcfromtimestamp(stat.st_ctime),
                    modified_date=datetime.utcfromtimestamp(stat.st_mtime),
                    mode=filemode(stat.st_mode)
                    )


def get_file_info(path, callback):
    stat = os.stat(path)
    return  callback(path, stat)


def walkdir(path, callback):
    """
    Walk thrue all files and folders in given path and call callback on them
    :param path: path
    :param callback: callback function takes two params: filepath and file stat
    :return:
    """
    res = []
    for f in os.listdir(path):
        filepath = os.path.join(path, f)
        res.append(get_file_info(filepath, callback))
    return res


# function to prevent directory traversal above basedir
def get_safe_path(basedir, request):
    data = request.json
    try:
        path = data["path"]
    except KeyError as e:
        return make_response(jsonify({"message": "Missing argument 'path'!"}), 403)

    fixed_path = os.path.normpath(os.sep + path).lstrip(os.sep)
    fullpath = os.path.abspath(os.path.realpath(os.path.join(basedir, fixed_path)))
    if not fullpath.startswith(os.path.abspath(os.path.realpath(basedir))):
        # return False
        raise ValueError("Path is outside of your basedir!")
    return fullpath


# I used POST method because parameters in URI of GET method shall have only ASCII char (not usable for filenames)
# And have params in GET method body/payload is not standart way
@app.route("/api/v1/file_system/list", methods=['POST'])
def ls_folder():
    safe_path = get_safe_path(BASEDIR, request)
    try:
        res = walkdir(safe_path, map_stat_to_meta)
    except FileNotFoundError as e:
        return make_response(jsonify({"message": "File not found!"}), 403)
    return jsonify([r._asdict() for r in res])


@app.route("/api/v1/file_system/info", methods=['POST'])
def get_meta():
    safe_path = get_safe_path(BASEDIR, request)
    try:
        res = get_file_info(safe_path, map_stat_to_meta)
    except FileNotFoundError as e:
        return make_response(jsonify({"message": "File not found!"}), 403)
    return jsonify(res._asdict())


# I used POST method because parameters in URI of DELETE method shall have only ASCII char (not usable for filenames)
# And have params in DELETE method body/payload is not standart way
@app.route("/api/v1/file_system/delete", methods=['POST'])
def delete():
    safe_path = get_safe_path(BASEDIR, request)
    if safe_path == BASEDIR:
        return make_response(jsonify({"message": "Can't remove root folder!"}), 403)

    try:
        if S_ISDIR(os.stat(safe_path).st_mode):
            os.rmdir(safe_path)
        else:
            os.remove(safe_path)
    except FileNotFoundError:
        return make_response(jsonify({"message": "File not found!"}), 403)
    except OSError:
        return make_response(jsonify({"message": "Directory not empty!"}), 403)
    return make_response(jsonify({"message": "Deleted"}), 200)


@app.route("/api/v1/file_system/create", methods=['POST'])
def create():
    safe_path = get_safe_path(BASEDIR, request)
    file_path, filename = os.path.split(safe_path)
    if not filename:
        return make_response(jsonify({"message": "Missing file name!"}), 403)
    if os.path.exists(safe_path):
        return make_response(jsonify({"message": "File already exist!"}), 403)
    os.makedirs(file_path, exist_ok=True)
    with open(safe_path, 'w') as fp:
        pass
    return jsonify(safe_path[len(BASEDIR):])


if __name__ == '__main__':
    app.run()
