############################################################
# Imports
############################################################
from collections import defaultdict
from collections import Counter
import math



############################################################
# Section 1: Hidden Markov Models
############################################################

def load_corpus(path):
    file = open(path)
    return [[tuple(token.split('=')) for token in line.split()] for line in file]
    pass

alpha = 1e-10
def prob(count_of_w, sum_of_words, num_vocabset_V):
    #probability_done = math.log((count_of_w + alpha) / (sum_of_words + alpha * (num_vocabset_V + 1.0)))
    #return probability_done
    probability_done =float(count_of_w + alpha) / float(sum_of_words + alpha * (num_vocabset_V + 1.0))
    return probability_done


class Tagger(object):
    """
    set of tags = {t1,t2, ...., tn}
    set of tokens = {w1, w2, ... , wn}
    pi(ti): begins with TAG ti.
    a(ti --> tj):TAG tj occurs after TAG ti
    b(ti --> wj): TOKEN wj is generated given TOKEN ti.
    """

    def __init__(self, sentences):
        # sentence = [('It','PRON'),('made','VERB'),('him','PRON'),('human','NOUN'),('.','.')]
        self.tags = ['NOUN', 'VERB', 'ADJ', 'ADV', 'PRON', 'DET', 'ADP', 'NUM', 'CONJ', 'PRT', '.', 'X']
        self.sentences = sentences

        sum_of_Tags = defaultdict(int)  # total count of tags or set of tags
        ini_pi = defaultdict(int)       # pi(ti) : probability that a sentence begins with tag ti
        tran_a = defaultdict(int)       # transition probabilities
        emiss_b = defaultdict(int)      # emission probabilities

        for sentence in self.sentences:
            ini_pi[sentence[0][1]] += 1 #init count
            for i in range(len(sentence)):
                emiss_b[(sentence[i][1], sentence[i][0])] += 1  # ex. emiss_b[('PRON','It')]=1
                sum_of_Tags[sentence[i][1]] += 1     #tag_count           # ex. {'DET': 137019, 'NOUN' : 275558 ,....}
                if i < len(sentence)-1:
                    tran_a[(sentence[i][1], sentence[i + 1][1])] += 1  # ex. {('PRON','VERB'):85838, (....} #tran_count


        # 1. initial tag probabilities: sentence begins with tag t
            # count_of_w = ini_pi[tag], sum_of_words = len(sentences), num_vocab_V = len(ini_pi)
            # self.ini_pi = tag , prob
        self.ini_pi = dict((tag_t, prob(ini_pi[tag_t], len(sentences), len(ini_pi))) for tag_t in ini_pi)
        #self.ini_pi['<UNK>'] = prob(0, len(sentences), len(ini_pi))

        # 2. transition probabilities:
        self.tran_a = defaultdict(float)
        a_counter = Counter(list(tran_a))  # vocabulary set
        for (t_i, t_j) in tran_a:
            self.tran_a[(t_i, t_j)] = prob(tran_a[(t_i, t_j)], sum_of_Tags[t_i], a_counter[t_i])
            self.tran_a[('<UNK>', t_j)] = prob(0, sum_of_Tags[t_i], a_counter[t_i])

        # 3. emission probabilities:
        self.emiss_b = defaultdict(float)
        b_counter = Counter(list(emiss_b))  # vocab size

        for (t, w) in emiss_b:
            self.emiss_b[(t, w)] = prob(emiss_b[(t, w)], sum_of_Tags[t], b_counter[t])  # ('DET', 'The'),0.0532
            self.emiss_b[('<UNK>', w)] = prob(0, sum_of_Tags[t], b_counter[t])

        pass



    def most_probable_tags(self, tokens):
        # Returns the list of the most probable tags corresponding to each input token.
        # argmax b(t --> w) . use emission probabilities
        checked_dicts = []

        #for word in tokens:  # vocabs = ('DET', 'The') , probability = 0.0532
        checked_dicts = [dict((vocabs, probability) for vocabs, probability in self.emiss_b.items() if vocabs[1] == word)for word in tokens]
            #dicts = [dict((vocabs, probability) for vocabs, probability in self.emiss_b.items() if vocabs[1] == token) for token in tokens]

        result = [max(dicts, key=dicts.get)[0] for dicts in checked_dicts]
        return result
        pass


    def viterbi_tags(self, tokens):  # obs of len T, state graph of len N
        # Viterbidecoding is a modification of the Forward algorithm, adapted to find the path of highest probability through the trellis graph containing all possible tag sequences
        # stage 1: first compute the probability of the most likely tag sequence
        # stage 2: reconstruct the sequence which achieves that probability from end to beginning by tracing backpointers.
        # initialize, recursion, termination.
        # CHECK SUDO CODE FROM MT27 PDF!!!!!!!!! & wikipedia

        V = [{} for i in range(len(tokens))]  # [{}, {}, {}, {}, {}]
        T = [{} for i in range(len(tokens))]

        for tag in self.tags:  # for each state s from 1 to N
            V[0][tag] = self.ini_pi[tag] * self.emiss_b[(tag, tokens[0])]  # viterbi[s,1] <- pi * bs(o_1)

        for t in range(1, len(tokens)):  # for each time step t from 2 to T
            for tag_j in self.tags:  # for each state s from 1 to N
                temp = []
                for tag in self.tags:
                    temp.append((V[t - 1][tag] * self.tran_a[(tag, tag_j)] * self.emiss_b[(tag_j, tokens[t])], tag))
                (V[t][tag_j], T[t][tag_j]) = max(temp)

        # termination step. end to beginning
        sequence = [max((V[-1][tag],tag) for tag in self.tags)[1]]

        for t in range(len(tokens)-1, 0 ,-1):
            sequence.append(T[t][sequence[-1]])

        result = reversed(sequence)
        return list(result)
        pass
