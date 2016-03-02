#include <exception>
#include <fstream>
#include <iostream>
#include <ostream>
#include <regex>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include <cassert>
#include <cstdlib>
#include <cmath>

#include <unistd.h> // POSIX getopt()


//------------------------------------------------------------------------------
// Shell interface
//------------------------------------------------------------------------------

struct program_arguments
{
    double compound_probability = 0;
    int ngram_length = 3;
    int number_of_words = 10;
    std::string constrained_prefix = "";
    std::string dictionary_filename = "";
    bool done = false;
};


/*
 * TODO
 */
void application_main(program_arguments const& args)
{
    (void) args;
}


/*
 * Prints usage message to the specified stream.
 */
void show_usage(std::ostream& out)
{
    out << R"USAGE(usage: pseudoword [-cgnpwh] [DICT]

Generate random pseudowords.

Argument:
 DICT       Sample words from this file (default: /usr/share/dict/words)

Options:
 -c PCOMP   Probability of forming compound word (default: 0)
 -g N       N of N-gram model (default: 3)
 -n NWORDS  Number of generated pseudowords (default: 10)
 -p PREFIX  Constrain generated pseudowords to start with this prefix
 -w WIDTH   Width of output at which lines should be wrapped
 -h         Print this message and exit
)USAGE";
}


/*
 * Parse command-line arguments.
 */
program_arguments parse_args(int argc, char** argv)
{
    program_arguments args;

    for (int optch; (optch = ::getopt(argc, argv, ":c:g:n:p:w:h")) != -1; )
    {
        switch (optch)
        {
          case 'c':
            args.compound_probability = std::stod(::optarg);
            break;

          case 'g':
            args.ngram_length = std::stoi(::optarg);
            break;

          case 'n':
            args.number_of_words = std::stoi(::optarg);
            break;

          case 'p':
            args.constrained_prefix = std::string{::optarg};
            break;

          case 'w':
            args.dictionary_filename = std::string{::optarg};
            break;

          case 'h':
            show_usage(std::cout);
            args.done = true;
            break;

          case ':':
            throw std::runtime_error("missing argument");

          case '?':
            throw std::runtime_error("unknown option");

          default:
            assert(false);
        }
    }

    return args;
}


/*
 * The program entry point.
 */
int main(int argc, char** argv)
{
    try
    {
        program_arguments const args = parse_args(argc, argv);
        if (!args.done)
            application_main(args);
    }
    catch (std::exception& e)
    {
        std::cerr << "error: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }
}
