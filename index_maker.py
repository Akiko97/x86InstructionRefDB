# -*- coding:UTF-8 -*-
import json

if __name__ == '__main__':
    with open('intrinsics.db.output.json', 'r') as f:
        intrinsics = json.load(f)
    with open('instructions.db.output.json', 'r') as f:
        instructions = json.load(f)
    index = []
    for section in instructions:
        for instruction in section['instructions']:
            data = {
                'mnemonic': instruction['mnemonic'].lower(),
                'summary': instruction['summary'],
                'table': instruction['data']['table']
            }
            matchingIntrinsics = [i for i in intrinsics
                                  if 'instruction' in i and i['instruction'] == data['mnemonic']]
            if len(matchingIntrinsics) == 0:
                data['set'] = 'N/A'
            else:
                data['set'] = matchingIntrinsics[0]['set']
                data['flags'] = matchingIntrinsics[0]['details']['synopsis']['value']['flags']
                data['intrinsics'] = []
                for intrinsic in matchingIntrinsics:
                    data['intrinsics'].append({
                        'id': intrinsic['id'],
                        'name': intrinsic['signature']['name'],
                        'signature': intrinsic['details']['synopsis']['value']['signature']
                        if intrinsic['details']['synopsis']['hasValue'] else '',
                        'description': intrinsic['details']['description']['value']
                        if intrinsic['details']['description']['hasValue'] else '',
                        'operation': intrinsic['details']['operation']['value']
                        if intrinsic['details']['operation']['hasValue'] else ''
                    })
            index.append(data)
    with open('index.db.output.json', 'w') as f:
        json.dump(index, f, indent=2)
