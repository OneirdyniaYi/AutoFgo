from aip import AipOcr

config = {
    'appId': '16904905',
    'apiKey': 'TPpmyZVC2OfIWf2g1NGqLAl2',
    'secretKey': 'zNgpj6QQLyOiOu4AWblL3GGdk2qTZpuz'
}

options = {}
options['probability'] = True

client = AipOcr(**config)


def get_file_content(file):
    with open(file, 'rb') as fp:
        return fp.read()


def img2str(image_path):
    image = get_file_content(image_path)
    result = client.basicGeneral(image, options)
    if 'words_result' in result:
        return '\n'.join([w['words'] for w in result['words_result']])


if __name__ == "__main__":
    res = img2str('屏幕截图 2019-07-29 10:16:24.png')
    print(res)
