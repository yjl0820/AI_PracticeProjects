############################################################
# Imports
############################################################
import email
from collections import defaultdict
import math
from os import listdir
from os.path import isfile, join


############################################################
# Section 1: Spam Filter
############################################################

def load_tokens(email_path):
    opened_file = open(email_path)
    message = email.message_from_file(opened_file)
    email_body = email.iterators.body_line_iterator(message)
    temp = [i for x in email_body for i in x.split()]
    return temp
    pass

def log_probs(email_paths, smoothing):
    vocabulary = [token for path in email_paths for token in load_tokens(path)]
    result = defaultdict(float)
    for token in vocabulary:
        result[token] += 1

    vocabulary_in_set = set(vocabulary)
    sum_of_words = len(vocabulary)
    alpha = smoothing
    num_vocabulary_V = len(vocabulary_in_set)
    for words in vocabulary_in_set: #words = vs
        result[words] = math.log((result[words] + alpha)/(sum_of_words + alpha * (num_vocabulary_V +1)))
        result["<UNK>"] = math.log(alpha/(sum_of_words + alpha * (num_vocabulary_V +1)))
    return result
    pass

class SpamFilter(object):

    def __init__(self, spam_dir, ham_dir, smoothing):
        spam_paths = [join(spam_dir, f) for f in listdir(spam_dir) if isfile(join(spam_dir, f))]
        ham_paths = [join(ham_dir, f) for f in listdir(ham_dir) if isfile(join(ham_dir, f))]

        self.spam_dict = log_probs(spam_paths, smoothing)
        self.ham_dict = log_probs(ham_paths, smoothing)

        self.p_spam = math.log(float(len(spam_paths))/(len(ham_paths)+len(spam_paths)))
        self.p_ham = 1 - self.p_spam
        pass


    def is_spam(self, email_path):
        vocabulary = load_tokens(email_path)
        prob_spam_sum = self.p_spam
        prob_ham_sum = self.p_ham
        for token in vocabulary:
            if token in self.spam_dict:
                prob_spam_sum += self.spam_dict[token]
            else:
                prob_spam_sum += self.spam_dict["<UNK>"]

            if token in self.ham_dict:
                prob_ham_sum += self.ham_dict[token]
            else:
                prob_ham_sum += self.ham_dict["<UNK>"]

        return prob_spam_sum >= prob_ham_sum
        pass


    def most_indicative_spam(self, n):
        #self.spam_dict = log_probs(spam_paths, smoothing)
        #self.ham_dict = log_probs(ham_paths, smoothing)
        # if word = win
        # P(W|S) = probability of the word "win" being in a spam message
            # = P(s|w) * P(w) / P(s)
        # P(S) = probability of a spam message overall
        # P(W) = probability of the word "win" in a message overall

        most_indicative_s = [] #tuple
        for token, log_prob in self.ham_dict.items():
            if token in self.spam_dict:
                result =log_prob - (math.log(math.exp(self.ham_dict[token]) + math.exp(self.spam_dict[token])))
            else:
                result = log_prob - (math.log(math.exp(self.ham_dict[token]) + math.exp(self.spam_dict["<UNK>"]))) #"UNK"
            most_indicative_s.append((token, result))

        most_indicative_s.sort(key=lambda x: x[1])
        output = list(map(lambda x: x[0],most_indicative_s))
        return output[:n]
        pass


    def most_indicative_ham(self, n):
        most_indicative_h = [] #tuple
        for token, log_prob in self.spam_dict.items():
            if token in self.ham_dict:
                result =log_prob - (math.log(math.exp(self.spam_dict[token]) + math.exp(self.ham_dict[token])))
            else:
                result = log_prob - (math.log(math.exp(self.spam_dict[token]) + math.exp(self.ham_dict["<UNK>"]))) #"UNK"
            most_indicative_h.append((token, result))

        most_indicative_h.sort(key=lambda x: x[1])
        output = list(map(lambda x: x[0],most_indicative_h))
        return output[:n]
        pass
