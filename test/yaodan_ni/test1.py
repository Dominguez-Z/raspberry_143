# -*- coding:utf-8 -*-import reimport osimport timeimport jsonimport codecsimport chardetdata = ''with codecs.open("new_data_format.json", 'r' ,encoding='utf-8') as f:    for line in f:        # dic = json.loads(line)        dic = line        #dic  = dic.encode('utf-8').decode('utf-8')        dic  = dic.encode('utf-8')#.decode('latin1')        dic = str(dic).replace('b\'','').replace('\\r\\n','').replace('\'','').replace(' ','')        dic = dic.encode('utf-8').decode('utf-8')        #print(type(dic))        #print(dic)        data = data + dic#print(data)#print(data)#data = data.encode("unicode-escape")#global false, null, true#false = null = true = ''data = eval(data)#print(data)#print(type(data))data=data['medicineList']['prescription_boxes']#print(data[2]['cells'][1]['pills'])#print(data[2]['cells'][1]['pills'][2]['medicine_name'])#print(len(data[2]['cells'][1]['pills']))#print(len(data[0]['cells'][0]['pills']))i=0j=0yao = []for x in range(len(data[0]['cells'][0]['pills'])):  #if x==0 or data[0]['cells'][0]['pills'][x]['medicine_name']  != data[0]['cells'][0]['pills'][x-1]['medicine_name'] :    yao.append([])    #print(data[0]['cells'][0]['pills'][x]['medicine_name'])    if x == 0 or data[0]['cells'][0]['pills'][x]['medicine_name'] != data[0]['cells'][0]['pills'][x - 1]['medicine_name']:     yao[x].append(data[0]['cells'][0]['pills'][x]['medicine_name'].encode('latin-1').decode('utf8'))#print(yao)for i in range(len(data)):    #box = []    for j in range(len(data[i]['cells'])):      for y in range(len(data[i]['cells'][j]['pills'])):        #print(i,j,y)        name=data[i]['cells'][j]['pills'][y]['medicine_name']        name = name.encode('latin-1').decode('utf8')        #print(name)        for x in range(len(data[0]['cells'][0]['pills'])):            name1 = data[0]['cells'][0]['pills'][x]['medicine_name']            name1 = name1.encode('latin-1').decode('utf8')            if name == name1:                yao[x].append((i,j))print(yao)