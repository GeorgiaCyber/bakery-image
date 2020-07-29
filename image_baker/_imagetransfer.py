from os import remove, stat
from subprocess import call
from tqdm import tqdm
from requests import get
from minio import Minio
from minio.error import ResponseError
import hashlib


class ImageDownload:
    def __init__(self, image_url):
        self.image_url = image_url

    def download_image(self):
        # Downloads image from url passed from download_url() if available
        file = self.image_url.split('/')[-1]
        file_request = get(self.image_url, stream=True, allow_redirects=True)
        total_size = int(file_request.headers.get('content-length'))
        initial_pos = 0

        print('\nDownloading image from ({}):'.format(self.image_url))
        with open(file, 'wb') as file_download:
            with tqdm(total=total_size, unit='it', unit_scale=True, desc=file, initial=initial_pos, ascii=True) as progress_bar:
                for chunk in file_request.iter_content(chunk_size=1024):
                    if chunk:
                        file_download.write(chunk)
                        progress_bar.update(len(chunk))

    def hash_download_image(self):
        # Create hash value for image downloaded with download_image()
        file = self.image_url.split('/')[-1]
        with open(file, 'rb') as file:
            content = file.read()
        sha = hashlib.sha256()
        sha.update(content)
        hash_file = sha.hexdigest()
        print('\nImage SHA256 Hash: {}'.format(hash_file))


class ImageUpload:
    def __init__(self, image_name, compressed_name, minioclientaddr, minioaccesskey, miniosecretkey, miniobucket):
        self.image_name = image_name
        self.compressed_name = compressed_name
        self.minioclientaddr = minioclientaddr
        self.minioaccesskey = minioaccesskey
        self.miniosecretkey = miniosecretkey
        self.miniobucket = miniobucket

    def uploadimagefile(self):
        print('\nUploading {} to minio object store at {}...'.format(self.compressed_name, self.minioclientaddr))
        client = Minio(self.minioclientaddr, access_key=self.minioaccesskey,
                       secret_key=self.miniosecretkey, secure=False)
        try:
            with open(self.compressed_name, 'rb') as file_data:
                file_stat = stat(self.compressed_name)
                client.put_object(self.miniobucket, self.compressed_name, file_data, file_stat.st_size)
        except ResponseError as err:
            print(err)
        remove(self.compressed_name)
        remove(self.image_name)
