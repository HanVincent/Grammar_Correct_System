# Error Ngram

The aim of this project is to generate error sentences from correct sentences given a large number of patterns.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
python 3.6+
nltk
spacy
```

### Installing

A step by step series of examples that tell you have to get a development env running

```
git clone https://github.com/NTHU-NLPLAB/error_ngram.git
```

### Run
Prepare your patterns file, and then run the following command.

1. gen_rules.py generates rules from the patterns.

```
python ./pattern_to_rule/gen_rules.py -i <input_file> -o <output_file>
```

2. After gaining your rule file, run this to modify all sentences.
```
python ./pattern_to_rule/gec.age.py [-c] -r <rule_file> -i <input_file> -o <output_file>
```

PS: If you want to combine two actions together, use `-c` option, which will first convert patterns to rules and then modify every sentence. On the other hand, just command `-i <file>` and `-o <file>`.

Use `-h` get instruction.

### TODO:
* Not implementing transfomation function such as add_Ving() or add_s.
