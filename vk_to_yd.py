import requests
from pprint import pprint
import datetime
import json
from tqdm import tqdm


class VK_GET:
    def __init__(self, token: str, user_id, version ='5.131'):
        self.token = token
        self.version = version
        self.user_id = user_id
        self.params = {
                       'access_token': self.token,
                       'v': self.version
                       }

    def get_json(self):
        URL = 'https://api.vk.com/method/photos.get'
        params = {
            'user_id': self.user_id,
            'album_id': 'profile',
            'rev': '1',
            'extended': '1',
            'access_token': self.token,
            'v': '5.131'
        }
        res = requests.get(URL, params=params).json()
        req = res['response']['items']
        return req

    def upload_photos_from_vk(self, count, name = "photo.json"):
        self.count = count
        req = self.get_json()
        names = self.get_names(count)
        my_photos = []
        photo_json = []
        sizes = []
        size_dict = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
        for i in req:
            file_url = max(i['sizes'], key=lambda x: size_dict[x["type"]])
            for f, o in file_url.items():
                if f == 'url':
                    my_photos.append(o)
            for k, v in file_url.items():
                if k == "type":
                    sizes.append(v)
        sizes = sizes[:count]
        for file_name, size in zip(names, sizes):
            photo_json.append({"file_name": file_name, "size": size})
        with open(name, 'w') as file:
            json.dump(photo_json, file)
        pprint(photo_json)
        my_photos = my_photos[:count]
        return my_photos

    def get_names(self, count):
        self.count = count
        req = self.get_json()
        likes = []
        now = datetime.datetime.now()
        for i in req:
            for k, v in i.items():
                if k == 'likes':
                    for c, l in v.items():
                        if c == 'count':
                            likes.append(f'{l}_likes_{now.strftime("%Y-%m-%d_%H-%M-%S")}.jpg')
        likes = likes[:count]
        return likes


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'OAuth {self.token}'}

    def create_folder(self, path):
        url_create = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        requests.put(f'{url_create}?path={path}', headers = headers)

    def upload_photos_to_yd(self, path, url_file, name):
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": f'/{path}/{name}', 'url': url_file, "overwrite": "true"}
        resp = requests.post(url, headers=headers, params=params)
        if resp.status_code != 200 and resp.status_code != 202:
            print(resp.status_code)


if __name__ == '__main__':
    with open('token_yd.TXT', 'r') as file_object:
        token_yd = file_object.read()
    with open('token_vk.TXT', 'r') as file_object:
        token_vk = file_object.read()
    user_id = 1
    files_to_yd = YaUploader(token_yd)
    files_from_vk = VK_GET(token_vk, user_id)
    path = 'photos'
    count = 5
    url_file = files_from_vk.upload_photos_from_vk(count)
    name = files_from_vk.get_names(count)
    result = files_to_yd.create_folder(path)
    for names, results in tqdm(zip(name, url_file)):
        files_to_yd.upload_photos_to_yd(path, results, names)




