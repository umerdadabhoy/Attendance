import os
import base64
def image_prep(path:str = r"media\images\logo_rak.png"):
    path_img = os.path.realpath(os.path.normpath(path))
    img_path = base64.b64encode(open(path_img, 'rb').read()).decode('utf-8')
    img_html = '<center><img src="data:image/png;base64,{0}"></center>'.format(img_path)
    return img_html


#print(img_html)


#print(image_prep())
#print(path_logo)