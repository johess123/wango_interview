import easyocr
reader = easyocr.Reader(['ch_sim','en'])
result = reader.readtext('test.jpg')
for (bbox, text, prob) in result:
    print(text)