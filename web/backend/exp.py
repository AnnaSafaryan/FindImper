from syntok.tokenizer import Tokenizer

# tok = Tokenizer()
# # optional: keep "n't" contractions and "-", "_" inside words as tokens
# text = "Да, и тут понятно, чё за… (Смеётся) Едь в (Пойково)."
# for token in tok.tokenize(text):
#     print(token)

# import syntok.segmenter as segmenter
# document = 'Да, и тут понятно, чё за... (Смеётся) Едь в (Пойково).'
# for paragraph in segmenter.process(document):
#     for sentence in paragraph:
#         for token in sentence:
#             # roughly reproduce the input,
#             # except for hyphenated word-breaks
#             # and replacing "n't" contractions with "not",
#             # separating tokens by single spaces
#             print(token.value, end=' ')
#         print()  # print one sentence per line
#     print()  # separate paragraphs with newlines


# from nltk.tokenize import sent_tokenize
# a = 'Да, и тут понятно, чё за… (Смеётся) Едь в (Пойково). Lf...'
# raw_sents = []
# for sent in sent_tokenize(a):
#     if '…' in sent:
#         raw_sents.extend([s for s in sent.split('…') if s])
#     elif '...' in sent:
#         raw_sents.extend([s for s in sent.split('...') if s])
#     else:
#         raw_sents.append(sent)
# print(raw_sents)


# from operator import add, sub
#
# filter_l_dict = {'пойми': ['хуй']}
# filter_r_dict = {'давай': ['.', ',', '!', '?', 'так', 'тогда']}
# filter_dict = {'left': filter_l_dict,
#                'right': filter_r_dict}
#
# def filter_words(part, i, filters):
#     word = part[i]
#     res = True
#     print(word)
#     sides = {'left': sub, 'right': add}
#     for side in sides:
#         if word in filters[side]:
#             print('YES')
#             try:
#                 oper = sides[side]
#                 near_tok = part[oper(i, 1)]
#                 if near_tok in filters[side][word]:
#                     res = False  # отфильтровали
#             except IndexError:
#                 print("!")
#                 res = True
#         else:
#             res = True
#     return res
#
# text1 = ['давай', ',', 'береги', 'себя', ',', 'на', 'связи', '!']
# print(filter_words(text1, 0, filter_dict))


# from pymorphy2 import MorphAnalyzer
# m = MorphAnalyzer()
# res_toks = m.parse('иду')
# res_tok = res_toks[0]
# # для полноты берём тот разбор, где есть императив
# for res in res_toks:
#     if res.tag.mood == 'impr':
#         res_tok = res
# print(res_tok.tag.tense)

# import re
# from pymystem3 import Mystem
# m = Mystem()
# text = ' '.join(
#     ['машина', 'поедет', 'говорю', '–', 'мне', 'скажешь', '.']
# )
# sent = m.analyze(text)
#
# def parse_gr(gr):
#     pos = re.findall(r'[A-Z]+=?', gr)[0].replace('=', '')
#     mood = re.findall(r'\bпов\b', gr)
#     if mood:
#         mood = mood[0]
#     else:
#         mood = ''
#     time = re.findall(r'\bнепрош\b', gr)
#     if time:
#         time = time[0]
#     else:
#         time = ''
#     more = []
#     more.extend(re.findall(r'\bприч\b', gr))
#     if more:
#         more = more[0]
#     else:
#         more = ''
#     return pos, mood, time, more
# for tok in sent:
#     try:
#         gr = tok['analysis'][0]['gr']
#         print(tok['text'])
#         print(gr)
#         print(parse_gr(gr))
#         print()
#     except:
#         pass


# from helpers.metrics.rouge import scoring
# h = ['None']
# r = ['None']
# print(scoring(r, h, 2))

# from json import load
# a = "C:\\Users\\annas\\YandexDisk\\Коды\\python 3\\Полина Экспертиза\\Повелительное\\data\\test\\data_1\\data_1_tok.txt"
# t = load(open(a))
# c = []
# for l in t['imps'].values():
#     for s in l:
#         if s:
#             c.append(s)
# print(len(c))

