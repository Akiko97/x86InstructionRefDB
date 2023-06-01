# -*- coding:UTF-8 -*-
import json


def i_filter(s):
    return ''.join(c for c in s if c.isalnum())


def match_string(target, input_string):
    input_words = input_string.lower().split()
    for word in input_words:
        if word == target:
            return True
    return False


def is_matching(i, d):
    if 'instruction' in i:
        inst = i_filter(i['instruction'])
        if inst == '':
            return False
        if inst == d['mnemonic']:
            return True
        table = d['table']
        for t in table:
            if t['type'] == 'table':
                items = t['value']['items']
                for item in items:
                    if 'instruction' in item and match_string(inst, item['instruction']):
                        return True
                    if 'opcodeinstruction' in item and match_string(inst, item['opcodeinstruction']):
                        return True
    return False


if __name__ == '__main__':
    with open('intrinsics.db.output.json', 'r') as f:
        intrinsics = json.load(f)
    with open('instructions.db.output.json', 'r') as f:
        instructions = json.load(f)
    with open('notFound.output.json', 'r') as f:
        notFound = json.load(f)
    index = []
    for section in instructions:
        for instruction in section['instructions']:
            data = {
                'mnemonic': instruction['mnemonic'].lower(),
                'summary': instruction['summary'],
                'table': instruction['data']['table'],
                'instruction-info': {}
            }
            for ti, t in enumerate(data['table']):
                if t['type'] == 'quote':
                    data['table'][ti]['value'] = data['table'][ti]['value'][1:] \
                        if data['table'][ti]['value'][0] == '\n' else data['table'][ti]['value']
            for k, v in instruction['data'].items():
                if k == 'table' or k == 'title':
                    continue
                else:
                    data['instruction-info'][k] = v
                    data['instruction-info'][k]['title'] = data['instruction-info'][k]['title'] \
                        .replace('\n\t\t\t\u00b6\n\t\t', '')
                    for iidi, iid in enumerate(data['instruction-info'][k]['data']):
                        if iid['type'] == 'quote':
                            data['instruction-info'][k]['data'][iidi]['value'] = iid['value'][1:] \
                                if iid['value'][0] == '\n' else iid['value']
            matchingIntrinsics = [i for i in intrinsics if is_matching(i, data)]
            if len(matchingIntrinsics) == 0:
                data['set'] = '-'
                data['flags'] = '-'
            else:
                dataSet = []
                for m in matchingIntrinsics:
                    if m['set'] not in dataSet:
                        dataSet.append(m['set'])
                data['set'] = ', '.join(dataSet) if len(dataSet) > 0 else '-'
                dataFlags = []
                for m in matchingIntrinsics:
                    if m['details']['synopsis']['value']['flags'] not in dataFlags:
                        dataFlags = list(set(dataFlags) | set(m['details']['synopsis']['value']['flags']))
                data['flags'] = ', '.join(dataFlags) if len(dataFlags) > 0 else '-'
                data['intrinsics'] = []
                for intrinsic in matchingIntrinsics:
                    ois = intrinsic['details']['synopsis']['value']['other_infos'] \
                        if intrinsic['details']['synopsis']['hasValue'] else []
                    for oii, oi in enumerate(ois):
                        ois[oii] = oi.replace('\u00a0', ' ')
                    data['intrinsics'].append({
                        'id': intrinsic['id'],
                        'name': intrinsic['signature']['name'],
                        'signature': intrinsic['details']['synopsis']['value']['signature']
                        if intrinsic['details']['synopsis']['hasValue'] else '',
                        'set': intrinsic['set'],
                        'flags': intrinsic['details']['synopsis']['value']['flags']
                        if intrinsic['details']['synopsis']['hasValue'] else [],
                        'other_infos': ois,
                        'description': intrinsic['details']['description']['value']
                        if intrinsic['details']['description']['hasValue'] else '',
                        'operation': intrinsic['details']['operation']['value']
                        if intrinsic['details']['operation']['hasValue'] else '',
                        'performance': intrinsic['details']['performance']['value']
                        if intrinsic['details']['performance']['hasValue'] else ''
                    })
            index.append(data)
    for nf in notFound:
        data = {
            'mnemonic': nf,
            'summary': '*Sorry, this instruction only contains intrinsics function details'
        }
        matchingIntrinsics = [i for i in intrinsics
                              if 'instruction' in i and i_filter(i['instruction']) == nf]
        data['set'] = matchingIntrinsics[0]['set']
        data['flags'] = matchingIntrinsics[0]['details']['synopsis']['value']['flags'] \
            if matchingIntrinsics[0]['details']['synopsis']['hasValue'] else ''
        data['intrinsics'] = []
        for intrinsic in matchingIntrinsics:
            data['intrinsics'].append({
                'id': intrinsic['id'],
                'name': intrinsic['signature']['name'],
                'signature': intrinsic['details']['synopsis']['value']['signature']
                if intrinsic['details']['synopsis']['hasValue'] else '',
                'set': intrinsic['set'],
                'flags': intrinsic['details']['synopsis']['value']['flags']
                if intrinsic['details']['synopsis']['hasValue'] else '',
                'other_infos': intrinsic['details']['synopsis']['value']['other_infos']
                if intrinsic['details']['synopsis']['hasValue'] else '',
                'description': intrinsic['details']['description']['value']
                if intrinsic['details']['description']['hasValue'] else '',
                'operation': intrinsic['details']['operation']['value']
                if intrinsic['details']['operation']['hasValue'] else ''
            })
        index.append(data)
    with open('index.db.output.json', 'w') as f:
        json.dump(index, f, indent=2)
