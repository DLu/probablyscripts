import numpy

IMAGE_EXTENSIONS = ['.jpg', '.png', '.jpeg', '.webp']
METADATA = '.image_metadata.yaml'


def get_images(input_directory):
    images = {}
    for filename in input_directory.glob('*.*'):
        if filename.name == METADATA:
            continue
        ext = filename.suffix.lower()
        if ext not in IMAGE_EXTENSIONS:
            print('Skipping ' + str(filename))
            continue
        images[filename.name] = filename
    return images


def get_center(im_meta):
    if 'center' in im_meta:
        return im_meta['center']
    elif im_meta.get('faces'):
        face = im_meta['faces'][0]
        center = {}
        for d in 'xy':
            center[d] = (face[f'{d}0'] + face[f'{d}1']) // 2
        return center
    else:
        return {'x': im_meta['width'] // 2, 'y': im_meta['height'] // 2}


def get_max_size(im_meta, center, aspect=None):
    crop_width = min(center['x'], im_meta['width'] - center['x'])
    crop_height = min(center['y'], im_meta['height'] - center['y'])

    if aspect is None:
        return crop_width, crop_height

    projected_height = int(crop_width * aspect)
    if projected_height > crop_height:
        return int(crop_height // aspect), crop_height
    else:
        return crop_width, projected_height


def get_box_size(im_meta, center, aspect=1.0):
    if 'zoom' in im_meta:
        return im_meta['zoom'], int(im_meta['zoom'] * aspect)
    else:
        return get_max_size(im_meta, center, aspect)


def get_box(im_meta, center, aspect=1.0):
    cw, ch = get_box_size(im_meta, center, aspect)

    return (center['x'] - cw,
            center['y'] - ch,
            center['x'] + cw,
            center['y'] + ch)


def auto_level(im, levels):
    hsv = im.convert('HSV')
    hsv_a = numpy.array(hsv)
    values = hsv_a[:, :, 2].flatten()
    histo = numpy.histogram(values, 256, (0, 256), density=True)[0]
    start = 0
    end = 255
    left_sum = histo[start]
    while left_sum < levels:
        start += 1
        left_sum += histo[start]
    right_sum = histo[end]
    while right_sum < levels:
        end -= 1
        right_sum += histo[end]
    hsv_pixels = hsv.load()
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            hue, sat, val = hsv_pixels[i, j]
            new_v = int(255 * (val - start) / (end - start))
            hsv_pixels[i, j] = (hue, sat, new_v)
    return hsv.convert('RGB')
