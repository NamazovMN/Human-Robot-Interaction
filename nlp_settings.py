from nltk import Tree
import spacy
from spacy.symbols import NOUN, PROPN
from spacy.matcher import Matcher


class NLP(object):
    def __init__(self):
        self.tokenizer = spacy.load("en_core_web_sm")
        self.matcher = Matcher(self.tokenizer.vocab)
        self.patterns = {'Double_Nouns': [{'POS': 'NOUN'}, {'POS': 'NOUN'}],
                         'Adjective_Noun': [{'POS': 'ADJ'}, {'POS': 'NOUN'}],
                         'Double_Pronouns': [{'POS': 'PROPN'}, {'POS': 'PROPN'}]}

    @staticmethod
    def tok_format(token_node: object) -> object:
        """
        The method processes the sentence and makes a tokenized structure
        :param token_node: node in the sentence
        :return:
        """
        return "_".join([token_node.orth_, token_node.tag_])

    def to_nltk_tree(self, node: object) -> object:
        """

        :param node: token's node in the sentence
        :return: nltk tree that shows the sentence structure. Example:
        I want to get shot of vodka and brandy.
                             want_VBP
                       _____________|________
                      |                   shot_NN
                      |      ________________|_______
                      |     |                      of_IN
                      |     |                        |
                      |   get_VB                  vodka_NN
                      |     |                 _______|_________
                    i_PRP to_TO            and_CC          brandy_NN
        """
        if node.n_lefts + node.n_rights > 0:
            return Tree(self.tok_format(node), [self.to_nltk_tree(child) for child in node.children])
        else:
            return self.tok_format(node)

    def extract_combinations(self, order_doc: object, type_combination: str) -> list:
        """
        The method extracts double combinations with respect to the given combination type through the order sentence
        :param order_doc:
        :param type_combination: type of double combinations in terms of POS (e.g., Double Nouns, Adjective Noun)
        :return: extracted combination according to the given type combination
        """
        pattern = self.patterns[type_combination]
        self.matcher.add(type_combination, None, pattern)
        matches = self.matcher(order_doc)
        combinations = [order_doc[start:end].text for (_, start, end) in matches]
        return combinations

    @staticmethod
    def collect_pos(order_doc: object) -> dict:
        """
        Method is used to collect nouns and proper nouns from the given order sentence.
        :param order_doc:
        :return: dictionary of nouns and proper nouns. Keys: nouns, propernouns,
                 Values: List of nouns, List of propernouns
        """
        nouns = [subject for subject in order_doc if subject.pos is NOUN]
        propernouns = [subject for subject in order_doc if subject.pos is PROPN]
        collection = {'nouns': nouns, 'propernouns': propernouns}

        return collection

    def collect_compounds(self, order_doc: object) -> list:
        """
        Method is used to collect all relevant data from the order that will be used to check the given order
        :param order_doc:
        :return: list of all possible identical combinations from the given order sentence
        """

        all_combinations = []
        for each in self.patterns.keys():
            temporary = []
            temporary += self.extract_combinations(order_doc, each)
            for drink in temporary:
                if drink not in all_combinations:
                    all_combinations.append(drink)

        return all_combinations

    @staticmethod
    def list_of_tokens(doc: object) -> list:
        """
        From the given sentence object each token is transformed to string and appended to the list of tokens
        :param doc: sentence object includes POS-tag and token
        :return: list of tokens in the string format
        """
        token_list = [str(each_token.text) for each_token in doc]

        return token_list
