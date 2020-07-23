# # -*- coding: utf-8 -*-
# import time

# def get_time():
#     time_str = time.strftime("%Y{}%m{}%d{} %X")
#     return time_str.format("年", "月", "日")


# if __name__ == "__main__":
#     print(get_time())
# import base64
# with open('./res/static/ship1.png', 'rb') as f:
#     # f.read()
#     # print(f.read())
#     b64 = base64.b64encode(f.read())
#     print(type(b64))

# def EncodeImg2B64Stream(imageid):
#     """
#     ????:
#     ??????base64?
#     :param imageid:???????id
#     :return: ???
#     """
#     import base64
#     img_stream = ''
#     with open('path_to_img/{}.png'.format(imageid), 'rb') as img_f:
#         img_stream = img_f.read()
#         img_stream = base64.b64encode(img_stream)
#     return img_stream