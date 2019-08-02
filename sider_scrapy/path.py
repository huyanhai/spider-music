import os
images_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'images')
if not os.path.exists(images_path):
  os.mkdir(images_path)
  print('没有imag文件夹')
else:
  print('有文件夹')
print(images_path)