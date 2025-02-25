from PIL import Image
import cv2
import numpy as np
import torchvision.transforms as transforms

def lprint(ms, log=None):
    '''Print message on console and in a log file'''
    print(ms)
    if log:
        log.write(ms+'\n')
        log.flush()

def resize_im(wo, ho, imsize=None, dfactor=1):
    wt, ht = wo, ho
    if imsize and max(wo, ho) > imsize and imsize > 0:
        scale = imsize / max(wo, ho)
        ht, wt = int(round(ho * scale)), int(round(wo * scale))

    # Make sure new sizes are divisible by the given factor
    wt, ht = map(lambda x: int(x // dfactor * dfactor), [wt, ht])
    scale = (wo / wt, ho / ht)
    return wt, ht, scale

def read_im(im_path, imsize=None):    
    im = Image.open(im_path)
    im = im.convert('RGB')

    # Resize
    wo, ho = im.width, im.height
    wt, ht, scale = resize_im(wo, ho, imsize=imsize)
    im = im.resize((wt, ht), Image.BICUBIC)
    return im, scale

def read_im_gray(im_path, imsize=None):
    im, scale = read_im(im_path, imsize)
    return im.convert('L'), scale

def load_gray_scale_tensor(im_path, device, imsize=None):
    im_rgb, scale = read_im(im_path, imsize)
    gray = np.array(im_rgb.convert('L'))
    gray = transforms.functional.to_tensor(gray).unsqueeze(0).to(device)
    return gray, scale

def load_im_tensor(im_path, device, imsize=None, normalize=True, with_gray=False,
                   raw_gray=False):
    im_rgb, scale = read_im(im_path, imsize)

    # RGB  
    im = transforms.functional.to_tensor(im_rgb)
    if normalize:
        im = transforms.functional.normalize(im , mean=[0.485, 0.456, 0.406], 
                                             std=[0.229, 0.224, 0.225])
    im = im.unsqueeze(0).to(device)
    
    if with_gray:
        # Grey
        gray = np.array(im_rgb.convert('L'))
        if not raw_gray:
            gray = transforms.functional.to_tensor(gray).unsqueeze(0).to(device)
        return im, gray, scale
    return im, scale

def read_im_gray_divisible(im_path, device, imsize=None, dfactor=1):
    im = cv2.imread(im_path, cv2.IMREAD_GRAYSCALE)

    # Resize
    ho, wo = im.shape
    wt, ht, scale = resize_im(wo, ho, imsize=imsize, dfactor=dfactor)
    im = cv2.resize(im, (wt, ht))
    im = transforms.functional.to_tensor(im).unsqueeze(0).to(device)
#     im = torch.from_numpy(im).float()[None] / 255  # (h, w) -> (1, h, w) and normalized
    return im, scale
