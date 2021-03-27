from default_settings import Settings
from bar_settings import Bar
from nlp_settings import NLP
import speech_recognition as sr

recognizer = sr.Recognizer()
microphone = sr.Microphone()
language = 'en'

# Menu
hot_drinks = ['black tea', 'green tea', 'jasmine', 'coffee',
              'cappuccino', 'latte', 'americano', 'espresso']
cold_drinks = ['ice tea', 'lemon juice', 'orange juice', 'cola', 'fanta',
               'apple juice', 'pineapple juice', 'sprite', 'vodka',
               'whiskey', 'jaeger', 'rom', 'brandy']

# Tea is used for preventing confusion if tea is not specified by ordering. Alcohol is used to ask the age.
tea = ['black tea', 'jasmine', 'green tea']
alcohol = ['vodka', 'whiskey', 'jaeger', 'rom', 'brandy']

another_order = 'Do you want to get something else?'
repeat = 'I could not understand. Could you please repeat it?'
goodbye = 'It was nice to have you. See you later!'
rejection = ['no thanks', 'no', 'nothing', 'thanks']

# definition of usable classes
nlp_settings = NLP()
settings = Settings(microphone, recognizer, language)
bar = Bar(settings, nlp_settings)
tokenizer = nlp_settings.tokenizer

# bar.introduction(cold_drinks, hot_drinks)


def get_proper_answer() -> object:
    order = settings.get_the_message()
    while not order:
        settings.speech_generator(repeat)
        order = settings.get_the_message()
    return tokenizer(order.lower())


while True:
    order_doc = get_proper_answer()
    check = bar.check_order(order_doc, rejection)

    while not check:
        settings.speech_generator(repeat)
        order_doc = get_proper_answer()
        check = bar.check_order(order_doc, rejection)

    try:
        [nlp_settings.to_nltk_tree(sentence.root).pretty_print() for sentence in order_doc.sents]
    except nlp_settings.UnknownValueError:
        print("Sentence was not properly processed")
    except nlp_settings.RequestError as e:
        print("Could not provide nltk tree; {0}".format(e))

    flag_rejection = bar.bot_response(order_doc, cold_drinks, hot_drinks, tea, alcohol, rejection)
    if flag_rejection:
        settings.speech_generator(goodbye)
        break
    else:
        settings.speech_generator(another_order)
