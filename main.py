from collections import defaultdict
from os import listdir
import random

import pymorphy2

block_symbols = ('*', '..', "глава")
max_words = 80
start_word_for_text = "пиво"
markov_words_context = 2
num_of_generated_sentences = 50

morph = pymorphy2.MorphAnalyzer()


def build_markov_chain(text: str) -> (defaultdict, list):
    words = text.split()
    markov_chain = defaultdict(list)
    for i in range(len(words) - markov_words_context):
        key = tuple(words[i:i + markov_words_context])
        next_word = words[i + markov_words_context]
        if not any(char.isdigit() for char in next_word):
            is_block_symbol_found = False
            for block_symbol in block_symbols:
                if block_symbol in next_word:
                    is_block_symbol_found = True
            if is_block_symbol_found:
                continue

            markov_chain[key].append(next_word)

    for i in markov_chain.keys():
        if str(i).isdigit() or not i:
            del markov_chain[i]

    variables = generate_start_variables(markov_chain)
    return markov_chain, variables


def generate_start_variables(markov_chain: defaultdict) -> list:
    if start_word_for_text:
        variables = []
        chain_keys = markov_chain.keys()
        normalized_start_word_for_text = morph.parse(start_word_for_text)[0].normal_form
        total_count = len(chain_keys)
        c = 0
        for key in chain_keys:
            key = tuple([morph.parse(word)[0].normal_form for word in key])
            if normalized_start_word_for_text in key:
                variables.append(key)
            c += 1
            print(f"{c}/{total_count}")
    else:
        variables = list(markov_chain.keys())

    return variables


def generate_sentence(chain: defaultdict, variables: list) -> str:
    if not chain:
        return ""

    start_key = random.choice(variables)
    sentence = list(start_key)

    for _ in range(max_words - markov_words_context):
        if start_key in chain:
            next_word = random.choice(chain[start_key])
            sentence.append(next_word)

            start_key = tuple(sentence[-markov_words_context:])
        else:
            break
    return " ".join(sentence)


def main():
    txt_dir = "txt_files"
    full_text = ''
    for file in listdir(txt_dir):
        try:
            with open(f"txt_files/{file}", encoding="cp1251") as f:
                text = f.read().lower()
                full_text += text
        except UnicodeDecodeError:
            pass

    markov_chain, variables = build_markov_chain(full_text)

    for sentence_number in range(num_of_generated_sentences):
        sentence = generate_sentence(markov_chain, variables)
        sentence = sentence.capitalize()
        print(f"{sentence_number + 1}. {sentence}")


if __name__ == "__main__":
    main()
