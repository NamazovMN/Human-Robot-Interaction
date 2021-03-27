import spacy
from spacy.symbols import NUM


class Bar(object):
    def __init__(self, settings, nlp):
        self.settings = settings
        self.nlp = nlp
        self.tokenizer = spacy.load("en_core_web_sm")

    @staticmethod
    def concatenate_menu(list_of_drinks: list) -> str:
        """
        concatenate_menu is called to merge all beverages in one sentence that will be used as informative speech.

        :param list_of_drinks: The list of drinks that can be offered
        :return: The drinks part of sentence which includes all beverages in order to present with voice
        """
        drink_sentence = ''
        for each_drink in list_of_drinks[:-1]:
            drink_sentence += each_drink + ', '
        drink_sentence += ' and ' + list_of_drinks[-1]
        print(drink_sentence)
        return drink_sentence

    def introduction(self, cold: list, hot: list) -> object:
        """
        introduction is the static method generates the informative sentences to inform the user. Resulting sentence
        is assigned and argument to speech generator which transform the sentence to speech.
        :return:
        """
        cold_sentence = self.concatenate_menu(cold)
        hot_sentence = self.concatenate_menu(hot)
        introduction_sentence = "Welcome to the bar. We can serve you hot and cold drinks as you wish! "
        intro_hot = "As a hot drink we have " + hot_sentence + ". "
        intro_cold = "If you want cold drink we can serve you " + cold_sentence + ". "
        introduction_sentence = introduction_sentence + intro_hot + intro_cold + "What would you like to have?"
        self.settings.speech_generator(introduction_sentence)

    @staticmethod
    def is_available(possible_drink: str, cold: list, hot: list) -> list:
        """
        Method check all possible combinations were extracted from the order that whether they are in the menu or not
        :param possible_drink: drink that extracted from the sentence (all possible combinations)
        :param cold: list of cold beverages
        :param hot: list of hot beverages
        :return: list of drinks that available in the menu
        """

        menu = cold + hot
        drink = [str(each_drink) for each_drink in possible_drink if str(each_drink) in menu]

        return drink

    @staticmethod
    def generate_answers(drink_list) -> str:
        """
        Generates default sentences according to the list of drinks was extracted from the order
        :param drink_list: list of drinks (strings)
        :return: sentence that will be used as an answer to user
        """
        length_order = len(drink_list)
        if length_order == 1:
            sentence = "Your " + drink_list[0] + " is coming right now!"
        elif length_order == 2:
            sentence = "You want to get " + drink_list[0] + " and " + drink_list[1] + \
                       ". They are coming right now!"
        else:
            multiple_drinks = ""
            for each_drink in drink_list[:-1]:
                multiple_drinks += drink_list[each_drink] + ", "
            multiple_drinks += " and " + drink_list[-1]
            sentence = "You have ordered " + multiple_drinks + ". They are coming right now!"
        return sentence

    def answer_to_the_order(self, drink_list, availability=True, case=0) -> str:
        """
        Generates sentences according to the user's orders and age.
        :param drink_list: list of drinks was extracted from the sentence of orders
        :param availability: boolean flag that shows whether drink is available in the menu or not
        :param case: case of scenarios which are:
                case = 0 : there is not an alcoholic drink in order.
                case = 1 : age is over 18, and all drinks are alcoholic.
                case = 2 : age is under 18, and all drinks are alcoholic.
                case = 3 : age is under 18, and there are alcoholic and other drinks.
        :return: sentence that bot tells to the user after the order
        """

        if case == 0:
            if availability:
                sentence = self.generate_answers(drink_list)
            else:
                sentence = "I am sorry, we are not selling it here!"

        elif case == 1:
            sentence = self.generate_answers(drink_list)

        elif case == 2:
            sentence = 'Your order contains only alcoholic beverages and we cannot ' \
                       'sell them to you because of your age!'

        elif case == 3:
            sentence_core = "We cannot sell to you alcoholic drinks you have ordered, " \
                            "because of your age. However, you have also ordered"
            sentence = sentence_core + self.generate_answers(drink_list)

        return sentence

    @staticmethod
    def check_alcohol(list_drink_doc, alcohol_drinks) -> list:
        """
        Gathers all alcoholic beverages from the list of drinks
        :param list_drink_doc: list of drinks is extracted from the order
        :return: list of tuple of alcoholic beverages (drink, index in main list)
        """
        alcohols = [(idx, str(each_drink)) for (idx, each_drink) in enumerate(list_drink_doc) if str(each_drink) in alcohol_drinks]
        return alcohols

    @staticmethod
    def delete_alcohols(list_drink, alcohols) -> list:
        """
        The method is used to delete the alcoholic drinks from the main list of orders
        :param list_drink: list of drinks was extracted from the order
        :param alcohols: list of tuples of alcoholic beverages and their indexes
        :return: new list which alcoholic beverages were discarded
        """
        temp_drinks = list_drink
        indexes = [each_idx for (each_idx, _) in alcohols]
        for each in sorted(indexes, reverse=True):
            del temp_drinks[each]
        return temp_drinks

    def check_order(self, order_doc, rejection) -> bool:
        """
        The method checks whether the order includes beverages or it is not order but gratitude!
        :param rejection: list of possible 'kind' rejections of ordering something
        :param order_doc: tokenized order
        :return: boolean result of whether sentence is order or not
        """
        flag_rejection = 0
        order_tokens = self.nlp.list_of_tokens(order_doc)

        for each in rejection:
            if each in order_tokens:
                flag_rejection = 1

        if not flag_rejection:
            collection = self.nlp.collect_pos(order_doc)
            drinks = self.nlp.collect_compounds(order_doc) + collection['nouns'] + collection['propernouns']
            if drinks:
                return True
            else:
                return False
        else:
            return True

    def ask_customer_age(self, list_drink, alcohols_raw) -> tuple:
        """
        The method filters the answer that bot will provide to user with respect to user's age
        :param alcohols_raw: list of alcohol beverages in the menu
        :param list_drink: the list of all beverages
        :return: filtered answer of the bot to user with respect to user's age
        """
        alcoholic_drinks = []
        case = 0
        alcohols = self.check_alcohol(list_drink, alcohols_raw)

        if not alcohols:
            case = 0
            return list_drink, case
        else:
            drinks_alc = ''
            if len(alcohols) == 1:
                sentence = "You have ordered " + alcohols[0][1] + \
                           ", which is alcoholic drink. Could you please tell me your age?"
            else:
                if len(alcohols) == 2:
                    sentence = "You have ordered " + alcohols[0][1] + " and " + alcohols[1][1] + \
                               ", which are alcoholic drinks. Could you please tell me your age?"
                else:
                    for each_alc in alcohols[:-1]:
                        drinks_alc += each_alc[1] + ', '
                    sentence = "You have ordered " + drinks_alc + " and " + alcohols[-1][1] + \
                               ", which are alcoholic drinks. Could you please tell me your age?"

            repeat_age = "Sorry, I could not understand. Could you please " \
                         "tell me how old are you ?"
            ans_age = ""
            self.settings.speech_generator(sentence)
            answer_age = self.settings.get_the_message()
            while answer_age is None:
                self.settings.speech_generator('Could you please repeat your age?')
                answer_age = self.settings.get_the_message()
            ans_age_doc = self.tokenizer(answer_age)

            while not ans_age_doc:
                self.settings.speech_generator(repeat_age)
                answer_age = self.settings.get_the_message()

            ans_age_doc = self.tokenizer(answer_age)
            ans_age = 0
            for each in ans_age_doc:
                if each.pos == NUM:
                    ans_age = int(str(each))

            if ans_age >= 18:
                alcoholic_drinks = list_drink
                case = 1
            else:
                if len(list_drink) is len(alcohols):
                    case = 2
                else:
                    case = 3
                alcoholic_drinks = self.delete_alcohols(list_drink, alcohols)

        return alcoholic_drinks, case

    def check_results(self, drinks, teas) -> bool:
        """
        The method is called when specific tea was asked from the user. If it is not understandable this method
        will be called and make user repeat the answer
        :param drinks: list of tokenized beverages from the main order
        :param teas: list of types of tea in the menu
        :return: flag whether bot understand the specified answer or not
        """
        for each in drinks:
            if str(each) in teas:
                return True
            else:
                self.settings.speech_generator('I could not understand. Could you please repeat?')
                return False

    def check_general_drinks(self, list_drink, tea_list) -> list:
        """
        The method is called, when user asked tea but not specified it. This will help user to be more specific.
        :param list_drink: list of beverage objects (they are not strings)
        :param tea_list: list of different types of tea
        :return: the merged list of other beverages (if there is) and specific tea rather than 'tea'
        """
        ask_specially = "Which kind of tea would you have? We are selling black tea, jasmine and green tea."

        list_drink_str = [str(each_drink) for each_drink in list_drink]
        possible_teas = [each for each in list_drink if str(each) in tea_list]
        if 'tea' in list_drink_str and not possible_teas:
            self.settings.speech_generator(ask_specially)

            drinks = self.check_answer_none()
            while not self.check_results(drinks, tea_list):
                drinks = self.check_answer_none()

            for each in list_drink_str:
                if each != "tea":
                    drinks.append(each)

            return drinks
        else:
            return list_drink_str

    def check_answer_none(self) -> list:
        """
        The method is used to check whether user's answer is None or not. It prevents the program to crash.
        :return: returns all drinks that ordered by user in a list
        """
        answer = self.settings.get_the_message()
        while answer is None:
            self.settings.speech_generator('I could not understand. Could you please repeat?')
            answer = self.settings.get_the_message()
        answer = answer.lower()

        answer_doc = self.tokenizer(answer)
        collection = self.nlp.collect_pos(answer_doc)
        drinks = self.nlp.collect_compounds(answer_doc) + collection['nouns'] + collection['propernouns']
        return drinks

    def bot_response(self, order_doc, cold_drinks, hot_drinks, tea_list, alcohols_list, rejection) -> int:
        """

        :param order_doc: tokenized object of user's order
        :param cold_drinks: list of cold drinks in the menu
        :param hot_drinks: list of hot drinks in the menu
        :param tea_list: list of types of tea in the menu
        :param alcohols_list: list of alcohols in the menu
        :param rejection: list of possible 'kind' rejections of ordering something
        :return: flag describes whether user wants to leave or to stay
        """
        flag_rejection = 0
        order_tokens = self.nlp.list_of_tokens(order_doc)

        for each in order_tokens:
            if each in rejection:
                flag_rejection = 1

        if flag_rejection == 1:
            return flag_rejection
        else:
            collection = self.nlp.collect_pos(order_doc)
            drinks = self.nlp.collect_compounds(order_doc) + collection['nouns'] + collection['propernouns']
            drink = self.check_general_drinks(drinks, tea_list)

            if self.is_available(drink, cold_drinks, hot_drinks):
                drink = self.is_available(drink, cold_drinks, hot_drinks)
                drink, case = self.ask_customer_age(drink, alcohols_list)
                sentence = self.answer_to_the_order(drink, case=case)
            else:
                drink, case = self.ask_customer_age(drink, alcohols_list)
                sentence = self.answer_to_the_order(drink, availability=False, case=case)

            self.settings.speech_generator(sentence)
            return flag_rejection
