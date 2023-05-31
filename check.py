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


if __name__ == '__main__':
    with open('intrinsics.db.output.json', 'r') as f:
        intrinsics = json.load(f)
    with open('instructions.db.output.json', 'r') as f:
        instructions = json.load(f)
    notFound = []
    for intrinsic in intrinsics:
        if 'instruction' in intrinsic and i_filter(intrinsic['instruction']) != '':
            instruction = i_filter(intrinsic['instruction'])
        else:
            continue
        found = False
        for section in instructions:
            instructionsInSection = section['instructions']
            for i in instructionsInSection:
                if i['mnemonic'].lower() == instruction:
                    found = True
                    break
                table = i['data']['table']
                for t in table:
                    if t['type'] == 'table':
                        items = t['value']['items']
                        for item in items:
                            if 'instruction' in item and match_string(instruction, item['instruction']):
                                found = True
                            if 'opcodeinstruction' in item and match_string(instruction, item['opcodeinstruction']):
                                found = True
                if found:
                    break
            if found:
                break
        if not found:
            if instruction not in notFound:
                notFound.append(instruction)
    print(str(len(notFound)) + ' instructions not found')
    with open('notFound.output.json', 'w') as f:
        json.dump(notFound, f, indent=2)
