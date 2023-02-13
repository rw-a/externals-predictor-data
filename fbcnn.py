"""To be used in Google Colab"""
import glob
import os.path
import logging
import torch
import cv2
from utils import utils_logger
from utils import utils_image as util
import requests


def main():
    quality_factor = 90
    input_path = "INPUT"
    output_path = "OUTPUT"
    model_name = 'fbcnn_color.pth'
    n_channels = 3            # set 1 for grayscale image, set 3 for color image

    nc = [64, 128, 256, 512]
    nb = 4

    result_name = model_name[:-4]
    util.mkdir(output_path)

    model_pool = 'model_zoo'  # fixed
    model_path = os.path.join(model_pool, model_name)
    if os.path.exists(model_path):
        print(f'loading model from {model_path}')
    else:
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        url = 'https://github.com/jiaxi-jiang/FBCNN/releases/download/v1.0/{}'.format(os.path.basename(model_path))
        r = requests.get(url, allow_redirects=True)
        print(f'downloading model {model_path}')
        open(model_path, 'wb').write(r.content)

    logger_name = result_name + '_qf_' + str(quality_factor)
    utils_logger.logger_info(logger_name, log_path=os.path.join(output_path, logger_name+'.log'))
    logger = logging.getLogger(logger_name)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # ----------------------------------------
    # load model
    # ----------------------------------------

    from models.network_fbcnn import FBCNN as net
    model = net(in_nc=n_channels, out_nc=n_channels, nc=nc, nb=nb, act_mode='R')
    model.load_state_dict(torch.load(model_path), strict=True)
    model.eval()
    for k, v in model.named_parameters():
        v.requires_grad = False
    model = model.to(device)
    logger.info('Model path: {:s}'.format(model_path))

    input_folders = {}
    for folder in os.listdir(input_path):
        input_folders[folder] = glob.glob(f"{input_path}/{folder}/*")
        if not os.path.exists(os.path.join(output_path, folder)):
            os.mkdir(os.path.join(output_path, folder))
    print(input_folders)

    index = 1
    for folder, image_paths in input_folders.items():
        for image_path in image_paths:
            img_name, ext = os.path.splitext(os.path.basename(image_path))
            logger.info('{:->4d}--> {:>10s}'.format(index, img_name+ext))
            image = util.imread_uint(image_path, n_channels=n_channels)

            if n_channels == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            _, encimg = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), quality_factor])
            image = cv2.imdecode(encimg, 0) if n_channels == 1 else cv2.imdecode(encimg, 3)
            if n_channels == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = util.uint2tensor4(image)
            image = image.to(device)

            output_image, QF = model(image)
            output_image = util.tensor2single(output_image)
            output_image = util.single2uint(output_image)

            util.imsave(output_image, os.path.join(output_path, folder, img_name+'.png'))
            index += 1


if __name__ == "__main__":
    main()
