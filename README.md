# Naive Bayesian

Download spaCy pre-trained Glove embedding weights

    # Discrete mode
    $ python naive_bayesian.py --mode=0

    # Continuous mode (using Gaussian)
    $ python naive_bayesian.py --mode=1


All options:
```
usage: naive_bayesian.py [-h] [--dir DIR] [--mode MODE] [--bin BIN]
                         [--num_classes NUM_CLASSES]

optional arguments:
  -h, --help            show this help message and exit
  --dir DIR             specify the data file
  --mode MODE           0 for discrete mode, 1 for continuous mode
  --bin BIN             specify the number of bins for discrete mode
  --num_classes NUM_CLASSES
                        specify the number of classes
```
