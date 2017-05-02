
# coding: utf-8

# In[1]:

from __future__ import unicode_literals, print_function
import json
import pathlib
import random

import spacy
from spacy.pipeline import EntityRecognizer
from spacy.gold import GoldParse
from spacy.tagger import Tagger
 
try:
    unicode
except:
    unicode = str


# In[2]:

def train_ner(nlp, train_data, entity_types):
    # Add new words to vocab.
    for raw_text, _ in train_data:
        doc = nlp.make_doc(raw_text)
        for word in doc:
            _ = nlp.vocab[word.orth]
#             print(_)

    # Train NER.
    ner = EntityRecognizer(nlp.vocab, entity_types=entity_types)
    for itn in range(5):
        random.shuffle(train_data)
        for raw_text, entity_offsets in train_data:
            doc = nlp.make_doc(raw_text)
            gold = GoldParse(doc, entities=entity_offsets)
            ner.update(doc, gold)
    return ner


# In[18]:

def save_model(ner, model_dir):
  
   
    model_dir = pathlib.Path(model_dir)
   
    if not model_dir.exists():
        print(model_dir)
        model_dir.mkdir()
    assert model_dir.is_dir()

    with (model_dir / 'config.json').open('wb') as file_:
        data = json.dumps(ner.cfg)
        if isinstance(data, unicode):
            data = data.encode('utf8')
        file_.write(data)
    ner.model.dump(str(model_dir / 'model'))
    if not (model_dir / 'vocab').exists():
        (model_dir / 'vocab').mkdir()
    ner.vocab.dump(str(model_dir / 'vocab' / 'lexemes.bin'))
    with (model_dir / 'vocab' / 'strings.json').open('w', encoding='utf8') as file_:
        ner.vocab.strings.dump(file_)


# In[20]:

def main(model_dir=None):
    #, parser=False, entity=False, add_vectors=False)
    nlp = spacy.load('en', parser=False, entity=False, add_vectors=False)
    # v1.1.2 onwards
    if nlp.tagger is None:
        print('---- WARNING ----')
        print('Data directory not found')
        print('please run: `python -m spacy.en.download --force all` for better performance')
        print('Using feature templates for tagging')
        print('-----------------')
        nlp.tagger = Tagger(nlp.vocab, features=Tagger.feature_templates)
    train_data = [
        (
            'I want to buy a Boxer',
            [(len('I want to buy a '), len('I want to buy a Boxer'), 'PRODUCT')]
        ),
        (
            'Do you have a Blanket',
            [(len('Do you have a '), len('Do you have Blanket'), 'PRODUCT')]
        ),
        (
            'Can you show me some Pants',
            [(len('Can you show me some '), len('Can you show me some Pants'), 'PRODUCT')]
        ),
        (
            'Show me some tops',
            [(len('Show me some '), len('Show me some tops'), 'PRODUCT')]
        ),
        
    ]
    ner = train_ner(nlp, train_data, ['PRODUCT'])

#     doc = nlp.make_doc('I want a Blanket')
#     nlp.tagger(doc)
#     ner(doc)
#     for word in doc:
#         print(word.text, word.orth, word.lower, word.tag_, word.ent_type_, word.ent_iob)
#     train_data = [
#         (
#             'Radha',
#             [(0, len('Radha'), 'PRODUCT')]
#         )
#         ]
#     ner = train_ner(nlp, train_data, ['PRODUCT'])  
#     doc = nlp.make_doc('where is London?')
#     nlp.tagger(doc)
#     ner(doc)
#     for word in doc:
#         print(word.text,word.ent_type_)
    

    if model_dir is not None:
        save_model(ner, model_dir)
    


# In[42]:

def predictEnt(query):
    nlp = spacy.load('en',parser=False)
    doc = nlp.make_doc(query)
    vocab_dir = pathlib.Path('ner/vocab')
    with (vocab_dir / 'strings.json').open('r', encoding='utf8') as file_:
        nlp.vocab.strings.load(file_)
    nlp.vocab.load_lexemes(vocab_dir / 'lexemes.bin')
    ner = EntityRecognizer.load(pathlib.Path("ner"), nlp.vocab, require=True)
    nlp.tagger(doc)
    ner(doc)
    for word in doc:
        if word.ent_type_=='PRODUCT':
            return word.text
        #print(word.text, word.orth, word.lower, word.tag_, word.ent_type_, word.ent_iob)
        


# In[48]:


if __name__ == '__main__':
    main('ner')
    ent=predictEnt('Do you have blankets')
    print(ent)
    # Who "" 2
    # is "" 2
    # Shaka "" PERSON 3
    # Khan "" PERSON 1
    # ? "" 2


# In[ ]:



