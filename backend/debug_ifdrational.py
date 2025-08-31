from image_metadata import extract_image_metadata

metadata = extract_image_metadata('test_images/DSC_0112.JPG')

def find_ifdrational(obj, path='root'):
    from PIL.TiffImagePlugin import IFDRational
    if isinstance(obj, dict):
        for k, v in obj.items():
            find_ifdrational(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_ifdrational(v, f'{path}[{i}]')
    elif 'IFDRational' in str(type(obj)):
        print(f'IFDRational found at {path}: {obj}')

find_ifdrational(metadata) 