"""
Program to generate random pseudowords based on an n-gram model learnt from
a dictionary file.

Examples
--------

Generate four random pseudowords:

    % python pseudoword.py -n 4
    spheatable
    soregia
    gaded
    shiosoprilin

Generate fourty random pseudowords packed in 60 columns:

    % python pseudoword.py -n 40 -w 60
    presperu bandispast scouncraff interrady helve nected
    metaxis pseudovulgulfmenotriform unmirele pyreness
    strewstonism unce straister tentorymate flowsheptuosis
    spenathite lycosis outer per masquadriliberrecludicileria

Generate four random pseudowords starting with unkn:

    % python pseudoword.py -n 4 -p unkn
    unknotte
    unknower
    unknotoxospostlinout
    unknoscal

Use this source code as the dictionary:

    % python pseudoword.py -n 4 pseudoword.py
    word
    nix
    poin
    parsert

"""
import argparse
import collections
import random
import re
import signal
import textwrap


# *nix has standard dictionary file. Let's use it by default.
DEFAULT_DICTFILE = '/usr/share/dict/words'

# Special characters used to indicate the beginning and the ending of a word.
WORD_PREFIX = '('
WORD_SUFFIX = ')'


#------------------------------------------------------------------------------
# Shell interface
#------------------------------------------------------------------------------

def main():
    """
    Entry point. This function loads dictionary file, learns word model, and
    generates random pseudowords based on the learnt model.
    """
    # Just terminate program with proper status code on receiving Ctrl-C.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    args = parse_args()

    words = load_words(args.dictfile)
    model = WordModel(words, args.N)
    pseudowords = []
    for _ in range(args.nwords):
        word = model.generate(args.prefix)
        while random.random() < args.pcompound:
            word += model.generate()
        pseudowords.append(word)
    display_words(pseudowords, args.width)


def load_words(filename):
    """
    Gather word samples in given text file.
    """
    words = []
    sep = re.compile('\W+')
    for line in open(filename):
        words.extend(sep.split(line))
    return [w.lower() for w in words if len(w) > 0]


def display_words(words, textwidth):
    """
    Print list of words.
    """
    if textwidth > 0:
        text = ' '.join(words)
        print('\n'.join(textwrap.wrap(text, width=textwidth)))
    else:
        for word in words:
            print(word)


def parse_args():
    """
    Parse command-line arguments: [-cgnpw] [dictfile].
    """
    parser = argparse.ArgumentParser(
        description='Random pseudoword generator.')

    # Optional arguments
    parser.add_argument(
        '-c', dest='pcompound', type=float, default=0,
        help='probability of forming a compound word (default: 0)')

    parser.add_argument(
        '-g', dest='N', type=int, default=3,
        help='N of N-gram (default: 3)')

    parser.add_argument(
        '-n', dest='nwords', type=int, default=10,
        help='number of pseudowords to generate (default: 10)')

    parser.add_argument(
        '-p', dest='prefix', type=str, default=None,
        help='constrained prefix of generated pseudoword (default: none)')

    parser.add_argument(
        '-w', dest='width', type=int, default=0,
        help='width of output at which lines should be wrapped (default: 0)')

    # Positional argument
    parser.add_argument(
        'dictfile', nargs='?', type=str, default=DEFAULT_DICTFILE,
        help='file containing word samples (default: %s)' % DEFAULT_DICTFILE)

    return parser.parse_args()


#------------------------------------------------------------------------------
# N-gram model
#------------------------------------------------------------------------------

class WordModel(object):
    """
    N-gram model of word.
    """
    def __init__(self, words, n):
        """
        Construct an n-gram model of word from word samples.

        Parameters
        ----------
        words : list
            List of sample words to learn.
        n : int
            The n of n-gram. Must be >= 2.
        """
        # Learn transition probabilities from the collocations of character
        # n-grams in the given list of words.
        collocations = []
        for word in words:
            word = WORD_PREFIX + word + WORD_SUFFIX
            ngrams = (word[i:i+n] for i in range(len(word) - n + 1))
            for pair in adjzip(ngrams):
                collocations.append(pair)

        transition_map = collections.defaultdict(lambda: [])
        for pair, count in collections.Counter(collocations).items():
            transition_map[pair[0]].append((pair[1], count))

        # Precompute the frequency of initial n-gram.
        prefix_weights = []
        for ngram in transition_map.keys():
            if ngram.startswith(WORD_PREFIX):
                freq = sum(count for _, count in transition_map[ngram])
                prefix_weights.append((ngram, freq))

        self._n = n
        self._transition_map = transition_map
        self._prefix_weights = prefix_weights


    def generate(self, prefix=None):
        """
        Generate a random word based on the model.

        Parameters
        ----------
        prefix : str | None
            If not None, generated pseudoword is constrained so that it starts
            with this prefix string. The prefix string must not be shorter than
            n characters where n is the number used to build the word model.
        """
        if prefix:
            prefix = WORD_PREFIX + prefix
        else:
            prefix = weighted_choice(self._prefix_weights)

        assert prefix.startswith(WORD_PREFIX)
        assert len(prefix) >= self._n

        word = prefix
        state = word[-self._n:]

        # Run a Markov chain Monte Carlo
        while not state.endswith(WORD_SUFFIX):
            state = weighted_choice(self._transition_map[state])
            word += state[-1]

        # Remove artificial prefix and suffix characters
        assert word.startswith(WORD_PREFIX) and word.endswith(WORD_SUFFIX)
        return word[1:-1]


#------------------------------------------------------------------------------
# Utilities
#------------------------------------------------------------------------------

def adjzip(it):
    """
    Generator producing pair of adjacent elements of given iterator.

    This generator iterates for each pair of adjacent elements of the given
    iterator just like `zip(it[:-1], it[1:])`, except that adjzip can handle
    one-pass iterators. Nothing is produced if the given iterator produces
    less than two elements.

    Parameters
    ----------
    it : iterator
        Arbitrary iterator.
    """
    first = True
    for x in it:
        if not first:
            yield prev, x
        first = False
        prev = x


def weighted_choice(wseq):
    """
    Randomly choose an element from a sequence with weights.

    Given sequence of (element, weight) pairs where weight is positive integer,
    this algorithm returns a randomly selected element using the weight value
    as the relative weight of choice.

    Parameters
    ----------
    wseq : sequence
        Arbitrary sequence of (element, weight) pairs. The weight must be a
        positive integer.
    """
    assert len(wseq) != 0
    rand = random.randrange(sum(weight for _, weight in wseq))
    cumsum = 0
    for elem, weight in wseq:
        cumsum += weight
        if rand < cumsum:
            return elem
    return elem


#------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
