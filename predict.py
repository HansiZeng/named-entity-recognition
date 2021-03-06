import os
import argparse
import spacy
import numpy as np
from keras.models import load_model
from dataset.data_processor import numericalize
from utils.serialization import load_object
from constants import NO_ENTITY_TOKEN, MAX_LEN_CHAR


def parse_args():
    parser = argparse.ArgumentParser(description='Script for using NER model')
    parser.add_argument('-p', '--path', help='Path to model and vocabulary directory.')

    args = parser.parse_args()
    # add path separator (/) at the end if needed
    args.path = args.path if args.path[-1] == os.path.sep else args.path + os.path.sep

    return args


def main():
    args = parse_args()

    vocabs = load_object(args.path + 'vocabs')
    model = load_model(args.path + 'model_ner')
    nlp = spacy.load('en')

    while True:
        user_input = input('Input sentence: ').strip()
        if not user_input:
            continue
        if user_input == 'end':
            break

        # tokenize user input
        doc = nlp(user_input)
        text = [token.text for token in doc]
        pos = [token.tag_ for token in doc]
        chars = numericalize(vocabs.chars, [[c for c in token.text] for token in doc], NO_ENTITY_TOKEN, maxlen=MAX_LEN_CHAR)
        chars = np.array(chars)[np.newaxis, :, :]

        # get model output
        # pad token is irrelevant here beacuse we are numericalizing just one sentence (it won't be padded)
        text = np.array(numericalize(vocabs.words, [text], NO_ENTITY_TOKEN))
        pos = np.array(numericalize(vocabs.pos, [pos], NO_ENTITY_TOKEN))

        out = model.predict([text, pos, chars]).squeeze()
        predicted_labels = [vocabs.labels.itos[label_idx] for label_idx in np.argmax(out, axis=1).tolist()]

        # print result
        for token, label in zip([token.text for token in doc], predicted_labels):
            print("%s %s" % (token, label))
        print()


if __name__ == '__main__':
    main()
