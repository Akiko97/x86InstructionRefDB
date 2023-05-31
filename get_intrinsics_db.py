# -*- coding:UTF-8 -*-
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

if __name__ == '__main__':
    data = []
    target = 'https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html'
    driver = webdriver.Firefox()
    driver.get(target)
    sleep(3)
    for i in range(2):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
    html = driver.page_source
    driver.quit()
    bf = BeautifulSoup(html, features='html.parser')
    intrinsicsList = bf.find(id='intrinsics_list')
    intrinsics = intrinsicsList.find_all('div', recursive=False)
    for intrinsic in intrinsics:
        intrinsicSet = intrinsic.get('class')[1]
        intrinsicId = intrinsic.get('id')
        intrinsicData = {
            'id': intrinsicId,
            'set': intrinsicSet
        }
        print('Handle intrinsic id = ' + str(intrinsicId))
        infos = intrinsic.find_all('div', recursive=False)
        for info in infos:
            infoClass = info.get('class')[0]
            if infoClass == 'instruction':
                intrinsicData['instruction'] = info.text
            elif infoClass == 'signature':
                rettype = info.find(class_='rettype')
                name = info.find(class_='name')
                signature = {
                    'rettype': rettype.text,
                    'name': name.text,
                    'param': []
                }
                param_types = info.find_all(class_='param_type')
                param_names = info.find_all(class_='param_name')
                if len(param_types) == len(param_names):
                    for index, param_name in enumerate(param_names):
                        signature['param'].append({
                            'type': param_types[index].text,
                            'name': param_name.text
                        })
                elif len(param_types) == 1 and len(param_names) == 0:
                    signature['param'].append({
                        'type': 'void'
                    })
                else:
                    print('Error: in param part in id: ' + str(intrinsicId))
                intrinsicData['signature'] = signature
            elif infoClass == 'details':
                details = {
                    'synopsis': {'title': 'Synopsis', 'hasValue': False},
                    'description': {'title': 'Description', 'hasValue': False},
                    'operation': {'title': 'Operation', 'hasValue': False},
                    'performance': {'title': 'Latency and Throughput', 'hasValue': False}
                }
                synopsis = info.find(class_='synopsis')
                if synopsis is not None:
                    details['synopsis']['hasValue'] = True
                    details['synopsis']['value'] = {}
                    sig = synopsis.find(class_='sig')
                    details['synopsis']['value']['signature'] = sig.text
                    sig.decompose()
                    details['synopsis']['value']['flags'] = []
                    cpuids = synopsis.find_all(class_='cpuid')
                    for cpuid in cpuids:
                        details['synopsis']['value']['flags'].append(cpuid.text)
                        cpuid.decompose()
                    for br in synopsis.find_all('br'):
                        br.replace_with('|')
                    parts = synopsis.get_text().split('|')
                    filtered_parts = [s for s in parts if s and 'CPUID' not in s]
                    details['synopsis']['value']['other_infos'] = filtered_parts
                description = info.find(class_='description')
                if description is not None:
                    details['description']['hasValue'] = True
                    details['description']['value'] = description.text
                operation = info.find(class_='operation')
                if operation is not None:
                    details['operation']['hasValue'] = True
                    details['operation']['value'] = operation.text
                performance = info.find(class_='performance')
                if performance is not None:
                    details['performance']['hasValue'] = True
                    details['performance']['value'] = str(performance)
                intrinsicData['details'] = details
            else:
                print('Error: Unknown info class in id: ' + str(intrinsicId))
        data.append(intrinsicData)
    with open('intrinsics.db.output.json', 'w') as file:
        json.dump(data, file, indent=2)
