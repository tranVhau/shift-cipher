import re
import json
import os
import itertools
from math import log
import wget
import zipfile


# wget.download("https://gist.githubusercontent.com/nguyenvanhieuvn/8d7c3440590a6db732ef6e05498c1566/raw/0164ccb7094b22a48a52844e7fa748cf2820cec9/all-vietnamese-syllables.txt(G%25C3%25B5%2520d%25E1%25BA%25A5u%2520ki%25E1%25BB%2583u%2520c%25C5%25A9)")

# wget.download(
#     "https://github.com/nguyenvanhieuvn/vn-accent-resoration/raw/master/test.txt")

# wget.download(
#     "https://github.com/nguyenvanhieuvn/vn-accent-resoration/raw/master/vn_en_nextwords.txt.zip")

# zip = zipfile.ZipFile('vn_en_nextwords.txt.zip')
# zip.extractall()

def remove_vn_accent(s):
    s = re.sub('[áàảãạăắằẳẵặâấầẩẫậ]', 'a', s)
    s = re.sub('[éèẻẽẹêếềểễệ]', 'e', s)
    s = re.sub('[óòỏõọôốồổỗộơớờởỡợ]', 'o', s)
    s = re.sub('[íìỉĩị]', 'i', s)
    s = re.sub('[úùủũụưứừửữự]', 'u', s)
    s = re.sub('[ýỳỷỹỵ]', 'y', s)
    s = re.sub('đ', 'd', s)
    return s


# Tạo bộ từ điển sinh dấu câu cho các từ không dấu
map_accents = {}
for word in open('vn_syllables.txt', encoding="utf8").read().splitlines():
    word = word.lower()
    no_accent_word = remove_vn_accent(word)
    if no_accent_word not in map_accents:
        map_accents[no_accent_word] = set()
    map_accents[no_accent_word].add(word)


# Đọc lm
lm = {}
for line in open('vn_en_nextwords.txt', encoding="UTF-8"):
    data = json.loads(line)
    key = data['s']
    lm[key] = data
vocab_size = len(lm)
total_word = 0


for word in lm:
    total_word += lm[word]['sum']

# tính xác suất dùng smoothing


def get_proba(current_word, next_word):
    if current_word not in lm:
        return 1 / total_word
    if next_word not in lm[current_word]['next']:
        return 1 / (lm[current_word]['sum'] + vocab_size)
    return (lm[current_word]['next'][next_word] + 1) / (lm[current_word]['sum'] + vocab_size)

# hàm beamsearch


def beam_search(words, k=3):
    sequences = []
    for idx, word in enumerate(words):
        if idx == 0:
            sequences = [([x], 0.0) for x in map_accents.get(word, [word])]
        else:
            all_sequences = []
            for seq in sequences:
                for next_word in map_accents.get(word, [word]):
                    current_word = seq[0][-1]
                    proba = get_proba(current_word, next_word)
                    # print(current_word, next_word, proba, log(proba))
                    proba = log(proba)
                    new_seq = seq[0].copy()
                    new_seq.append(next_word)
                    all_sequences.append((new_seq, seq[1] + proba))
            # print(all_sequences)
            all_sequences = sorted(
                all_sequences, key=lambda x: x[1], reverse=True)
            sequences = all_sequences[:k]
    return sequences

# tiền xử lý text


def preprocess(sentence):
    sentence = sentence.lower()
    sentence = re.sub(r'[.,~`!@#$%\^&*\(\)\[\]\\|:;\'"]+', ' ', sentence)
    sentence = re.sub(r'\s+', ' ', sentence).strip()
    return sentence


sentence = "qua le"
sentence = preprocess(sentence)
_sentence = remove_vn_accent(sentence)
words = _sentence.split()
results = beam_search(words, k=5)
print('INP:', sentence)

print('OUT:', ' '.join(results[0][0]))
print('CMP:', ' '.join(results[0][0]) == sentence)
