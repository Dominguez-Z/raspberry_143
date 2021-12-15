import codecs

def updata_yao():
    with codecs.open("yaowu_md.txt", 'r', encoding='utf-8') as f1:
        yaowu_md = f1.read()
    #print(yaowu)
    with codecs.open("yaowu_wz.txt", 'r', encoding='utf-8') as f2:
        yaowu_wz = f2.read()
    #print(type(yaowu_md),type(yaowu_wz))
    yaowu_md = yaowu_md.split(",")
    yaowu_wz = eval(yaowu_wz)
    return yaowu_md,yaowu_wz

global wei
wei=[0,0]
global yaowu_md
global yaowu_wz
yaowu_md,yaowu_wz = updata_yao()


def json2list():
    data = ''
    with codecs.open("new_data_format.json", 'r', encoding='utf-8') as f:
        for line in f:
            dic = line
            dic = dic.encode('utf-8')
            dic = str(dic).replace('b\'', '').replace('\\r\\n', '').replace('\'', '').replace(' ', '')
            dic = dic.encode('utf-8').decode('utf-8')
            data = data + dic
    data = eval(data)
    data = data['medicineList']['prescription_boxes']
    yao = []
    for x in range(len(data[0]['cells'][0]['pills'])):
        yao.append([])
        if x == 0 or data[0]['cells'][0]['pills'][x]['medicine_name'] != data[0]['cells'][0]['pills'][x - 1][
            'medicine_name']:
            yao[x].append(data[0]['cells'][0]['pills'][x]['medicine_name'].encode('latin-1').decode('utf8'))
    while [] in yao:
        yao.remove([])
    #print(yao)
    for i in range(len(data)):
        for j in range(len(data[i]['cells'])):
            for y in range(len(data[i]['cells'][j]['pills'])):
                name = data[i]['cells'][j]['pills'][y]['medicine_name']
                name = name.encode('latin-1').decode('utf8')
                for x in range(len(yao)):
                    name1 = data[0]['cells'][0]['pills'][x]['medicine_name']
                    name1 = name1.encode('latin-1').decode('utf8')
                    if name == name1:
                        yao[x].append((i, j))
    #print(yao)
    return yao



yao = json2list()
print(yao)
for i in range(len(yao)):
    yao1 = yao[i][0]
    #print(yao1)
    num = yaowu_md.index(yao1)
    #print(num)
    a = num//8
    b = num%8
    #wz = yaowu_wz[str(a)+'-'+str(b)]
    #print(wz)
    print(a,b)

print("结束")
