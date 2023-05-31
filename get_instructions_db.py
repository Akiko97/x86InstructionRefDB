# -*- coding:UTF-8 -*-
import requests
import json
import re
from bs4 import BeautifulSoup


# 由表格标题自动生成prop
def gen_prop(s):
    s = re.sub(r'\W+', '', s)
    s = s.lower()
    return s


# 判断元素是否是header
def is_header(ele_type):
    return bool(re.match(r'h[1-6]$', ele_type))


if __name__ == '__main__':
    # data是最终数据
    data = []
    target = 'https://www.felixcloutier.com/x86/'
    payload = {}
    req = requests.get(url=target, params=payload)
    req.encoding = 'UTF-8'
    html = req.text
    bf = BeautifulSoup(html, features='html.parser')
    # 获取所有标题和对应的表格
    sections = bf.find_all('h2')
    tables = bf.find_all('table')
    # 将每个表格中的指令分别存储在allInstructions的子数组中
    allInstructions = []
    # 这里开始分别处理每个大表格
    for table in tables:
        # 将每个表格中的全部指令存在instructions中
        instructions = []
        # 获取表格每一行后删除第一行标题，剩下的每一行都对应一个指令
        rows = table.find_all('tr')
        del rows[0]
        # 处理每一行的指令
        for row in rows:
            # 表格的第一列是助记符，第二列是描述，将其存储在instruction中
            cols = row.find_all('td')
            mnemonic = cols[0].a.text
            summary = cols[1].text
            instruction = {'mnemonic': mnemonic, 'summary': summary}
            # 输出正在处理的指令助记符
            print('Get mnemonic: ' + mnemonic)
            # 获取正在处理的指令的详情页面
            href = cols[0].a.get('href')[2:]
            subTarget = target + href
            subReq = requests.get(url=subTarget)
            subReq.encoding = 'UTF-8'
            subHtml = subReq.text
            subBf = BeautifulSoup(subHtml, features='html.parser')
            # 获取页面的body，删除页眉和页脚，剩下的全部为正文内容
            body = subBf.body
            rmElements = body.find_all(['header', 'footer'])
            for rmElement in rmElements:
                rmElement.decompose()
            # 新建指令详细数据的词典，其中一定包含title和table两项
            instructionData = {'title': '', 'table': []}
            # 正在处理的数据名称，初识设为空（包括了大标题和指令Opcode的表格，可能包含针对表格内容的详细解释）
            dataAttribute = ''
            # 遍历页面中的所有元素，更新instructionData
            for index, element in enumerate(body.children):
                # 获取当前element的类型，如果是None（无内容）则直接跳过
                eleType = element.name
                if eleType is None:
                    continue
                # 获取当前element的id
                eleId = element.get('id')
                # 如果包含element为包含id的标题（h1, h2, h3...），使用id更新dataAttribute
                # 并使用dataAttribute新建一个数组用来保存该项开始到下一个id标题结束的全部element
                if eleId is not None and is_header(eleType):
                    dataAttribute = eleId
                    instructionData[dataAttribute] = {
                        'title': element.text,
                        'data': []
                    }
                    continue
                # 使用index为0的无id的h1内容来更新instructionData.title
                if index == 0 and eleType == 'h1':
                    instructionData['title'] = element.text
                    continue
                # 分类处理数据，将数据存储在eleData中
                eleData = {'type': ''}
                if eleType == 'p':
                    eleData['type'] = 'string'
                    eleData['value'] = element.text
                elif eleType == 'pre':
                    eleData['type'] = 'code'
                    eleData['value'] = element.text
                elif eleType == 'table':
                    # 第一个table保存为自定义表格类型
                    if dataAttribute == '':
                        eleData['type'] = 'table'
                        eleTableRows = element.find_all('tr')
                        # 表头由表格第一行确定
                        eleTableTitles = eleTableRows[0].find_all('th')
                        eleTableTitles = eleTableRows[0].find_all('td') \
                            if len(eleTableTitles) == 0 else eleTableTitles
                        tableTitle = []
                        for eleTableTitle in eleTableTitles:
                            tableTitle.append({
                                'label': eleTableTitle.text,
                                'prop': gen_prop(eleTableTitle.text)
                            })
                        # 获取表头后，删除表格第一行，方便后面获取表内数据
                        del eleTableRows[0]
                        # 获取表内数据
                        tableItems = []
                        for eleTableRow in eleTableRows:
                            eleTableRowData = {}
                            eleTableCols = eleTableRow.find_all('td')
                            for i, eleTableCol in enumerate(eleTableCols):
                                eleTableRowData[tableTitle[i]['prop']] = eleTableCol.text
                            tableItems.append(eleTableRowData)
                        # 将表头和数据插入value中
                        eleData['value'] = {
                            'title': tableTitle,
                            'items': tableItems
                        }
                    # 其余表格保存为html原生表格类型
                    else:
                        eleData['type'] = 'html-table'
                        eleData['value'] = str(element)
                elif eleType == 'figure':
                    eleData['type'] = 'figure'
                    eleData['value'] = str(element)
                elif eleType == 'blockquote':
                    eleData['type'] = 'quote'
                    eleData['value'] = element.text
                elif eleType == 'ul':
                    eleData['type'] = 'list'
                    eleData['value'] = []
                    lis = element.find_all('li')
                    for li in lis:
                        eleData['value'].append(li.text)
                elif eleType == 'svg':
                    eleData['type'] = 'svg'
                    eleData['value'] = str(element)
                elif eleType == 'figcaption':
                    eleData['type'] = 'caption'
                    eleData['value'] = element.text
                else:
                    print('Unknown type ' + eleType + ' in ' + mnemonic)
                # 如果index大于0但是处于第一个含有id的元素之前（dataAttribute为空），
                # 将eleData插入到instructionData.table中
                if index > 0 and dataAttribute == '':
                    instructionData['table'].append(eleData)
                # 如果包含了dataAttribute（在两个header中间的情况），
                # 将eleData插入到instructionData.dataAttribute中
                else:
                    instructionData[dataAttribute]['data'].append(eleData)
            # 已经写入全部的instructionData，将指令详细数据存储在instruction中
            instruction['data'] = instructionData
            # 将该条指令插入到该表格的全部指令数组instructions中
            instructions.append(instruction)
        # 把该表格的instructions插入到总allInstructions中
        allInstructions.append(instructions)
    # 如果标题的数目和指令表格的数目相同，存储data到文件中
    if len(sections) == len(allInstructions):
        for index, section in enumerate(sections):
            data.append({'section': section.text, 'instructions': allInstructions[index]})
        with open('instructions.db.output.json', 'w') as file:
            json.dump(data, file, indent=2)
