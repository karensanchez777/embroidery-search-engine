import os
import cv2
import torch
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from adet.config import defaults


cfg = get_cfg()
cfg.set_new_allowed(True)
cfg.merge_from_file("configs/attn_R_50.yaml")
cfg.MODEL.WEIGHTS = "models/tt_e2e_attn_R_50.pth"
cfg.MODEL.DEVICE = "cpu"

predictor = DefaultPredictor(cfg)

def decode_recognition_batch(recs_tensor, voc_size=96, custom_dict_path=None):
    """
    Decode a batch of recognition tensors into strings.

    Args:
        recs_tensor (torch.Tensor or numpy.ndarray): shape (N, L) where N is number of instances.
        voc_size (int): vocabulary size used in the model config (typically 96 for ABCNet).
        custom_dict_path (str): path to a pickle file with custom CTLABELS. If None, default is used.

    Returns:
        List[str]: decoded text for each instance
    """
    if isinstance(recs_tensor, torch.Tensor):
        recs_tensor = recs_tensor.cpu().numpy()
    
    if custom_dict_path is not None:
        import pickle
        with open(custom_dict_path, 'rb') as fp:
            CTLABELS = pickle.load(fp)
    else:
        CTLABELS = [' ','!','"','#','$','%','&','\'','(',')','*','+',',','-','.','/',
                    '0','1','2','3','4','5','6','7','8','9',':',';','<','=','>','?',
                    '@','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P',
                    'Q','R','S','T','U','V','W','X','Y','Z','[','\\',']','^','_','`','a',
                    'b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r',
                    's','t','u','v','w','x','y','z','{','|','}','~']

    def decode_single(rec):
        s = ''
        for c in rec:
            c = int(c)
            if c < voc_size - 1:
                s += CTLABELS[c]
            elif c == voc_size - 1:
                s += u'口'  # special token or padding
        return s

    return [decode_single(rec) for rec in recs_tensor]

def ABCNetPredictions(img_filepath):
    """
    Perform OCR on an image using ABCNet from AdelaiDet.

    Args:
        img_filepath (str): Path to the input image.

    Returns:
        List[str]: Recognized text strings from the image.
    """
    if not os.path.isfile(img_filepath):
        raise FileNotFoundError(f"Image file not found: {img_filepath}")

    img = cv2.imread(img_filepath)
    if img is None:
        raise ValueError(f"Failed to read image from: {img_filepath}")

    predictions = predictor(img)
    if 'instances' not in predictions or not hasattr(predictions['instances'], 'recs'):
        return []

    recs = predictions['instances'].recs
    decoded_texts = decode_recognition_batch(recs)
    return decoded_texts