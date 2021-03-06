import argparse
import dataset
import numpy as np


class NaiveBayesian(object):
    """
    Implement the discrete naive bayesian classifier
    Tally the frequency of the values of each pixel into 32 bins
    """

    def __init__(self, num_features, num_classes, num_bins):
        self.num_features = num_features
        self.num_classes = num_classes
        self.num_bins = num_bins

    def train(self, train_images, train_labels):
        print('[+] Training starts ...')

        N = train_images.shape[0]
        self.prior = np.array([(train_labels == i).sum()/N for i in range(self.num_classes)], dtype=np.float) # count # of samples for each label

        # Training
        self.p = np.zeros((self.num_classes, self.num_features, self.num_bins))
        for i in range(N):
            if i % 2000 == 0:
                print("[*] Processing %d images" % i)

            for d in range(self.num_features):
                # Assign # of bin for each pixel
                _bin = int(train_images[i][d] // (256/self.num_bins))
                self.p[int(train_labels[i])][d][_bin] += 1

        # Calculate the distribution for each pixel
        for i in range(10):
            for d in range(self.num_features):
                for b in range(self.num_bins):
                    if self.p[i][d][b] == 0:
                        self.p[i][d][b] += 0.0001

                    self.p[i][d] /= self.p[i][d].sum()

        print("[-] Training finished ...\n")

    def inference(self, test_images, test_labels, N, print_num=10):
        log_posterior = np.zeros((N, 10))
        predictions = np.zeros(N)

        print('[+] Testing starts ...')

        log_prior = np.log(self.prior)
        for i in range(N):
            if i % 1000 == 0:
                print("[*] Test %d images" % i)

            # Calculate the log likelihood given the class
            log_likelihood = np.zeros(len(log_prior))
            for l in range(self.num_classes):
                # Aussme pixels are independent to each other
                for d in range(self.num_features):
                    _bin = int(test_images[i][d] // int(256//self.num_bins))
                    log_likelihood[l] += np.log(self.p[l][d][_bin])

            log_posterior[i] = log_likelihood + log_prior
            predictions[i] = np.argmax(log_posterior[i])

        print("\n[+] ---------- %d Prediction Results ----------" % print_num)
        for i in range(print_num):
            print("log_posterior: [", end='')
            for j in range(log_posterior.shape[1]-1):
                print('{0:0.2f}, '.format(log_posterior[i][j]), end='')
            print('{0:0.2f}]'.format(log_posterior[i][-1]))

            print("prediction: %d   true label: %d\n" % (predictions[i], test_labels[i]))

        accuracy = np.sum(predictions==test_labels[:N]) / N

        return predictions, 1 - accuracy


class GaussianNaiveBayesian(object):

    def __init__(self, num_features, num_classes):
        self.num_features = num_features
        self.num_classes = num_classes

        self.mean = np.zeros((num_classes, num_features))
        self.variance = np.zeros((num_classes, num_features))

    def train(self, train_images, train_labels):
        print("[+] Training starts ...")

        N = train_images.shape[0]
        N_l = np.array([(train_labels == i).sum() for i in range(self.num_classes)], dtype=np.float) # count # of samples for each label
        self.prior = N_l / N

        # Udpate mean of Gaussian
        for c in range(self.num_classes):
            _sum = np.sum(train_images[n] if train_labels[n] == c else 0.0 for n in range(N))  # _sum shape = (784,)
            self.mean[c] = _sum / N_l[c]

        # Update variance of Gaussian
        for c in range(self.num_classes):
            _sum = np.sum((train_images[n] - self.mean[c])**2 if train_labels[n] == c else 0.0 for n in range(N))
            self.variance[c] = _sum / N_l[c]

        print("[-] Training finished ...\n")

    def inference(self, test_images, test_labels, N, print_num=10):
        log_posterior = np.zeros((N, 10))
        predictions = np.zeros(N)

        print('[+] Testing starts ...')

        for i in range(N):
            if i % 1000 == 0:
                print("[*] Test %d images" % i)

            log_posterior[i] = self.classify(test_images[i])
            predictions[i] = np.argmax(log_posterior[i])

        print("\n[+] ---------- %d Prediction Results ----------" % print_num)
        for i in range(print_num):
            print("log_posterior: [", end='')
            for j in range(log_posterior.shape[1]-1):
                print('{0:0.2f}, '.format(log_posterior[i][j]), end='')
            print('{0:0.2f}]'.format(log_posterior[i][-1]))

            print("prediction: %d   true label: %d\n" % (predictions[i], test_labels[i]))

        accuracy = np.sum(predictions==test_labels[:N]) / N

        return log_posterior, 1 - accuracy

    def classify(self, image):
        result = [self._log_probability(image, _class) for _class in range(self.num_classes)]

        return np.array(result)

    def _log_probability(self, x, c):
        log_prior_c = np.log(self.prior[c])

        log_likelihood = 0.0
        for d in range(self.num_features):
            log_likelihood += np.log(self._gaussian(x[d], self.mean[c][d], self.variance[c][d]))

        return log_prior_c + log_likelihood

    def _gaussian(self, x, u, var):
        if var < 1e-6:
            return 0.0001

        return (1 / np.sqrt(2 * np.pi * var)) * np.exp(-np.power((x - u), 2) / (2*var))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='specify the data file', default='data')
    parser.add_argument('--mode', type=int, help='0 for discrete mode, 1 for continuous mode', default=0)
    parser.add_argument('--bin', type=int, help='specify the number of bins for discrete mode', default=32)
    parser.add_argument('--num_classes', type=int, help='specify the number of classes', default=10)
    parser.add_argument('--num_test', type=int, help='specify the number of images being tested', default=10000)
    args = parser.parse_args()

    # Load dataset
    train_images, train_labels, test_images, test_labels = dataset.load_mnist_dataset(args.dir)

    if args.mode == 0:
        # discrete mode
        print('------ Discrete Naive Bayesian Classifier ------')
        model = NaiveBayesian(train_images.shape[1], args.num_classes, args.bin)
    elif args.mode == 1:
        # continuous mode
        print('------ Gaussian Naive Bayesian Classifier ------')
        model = GaussianNaiveBayesian(train_images.shape[1], args.num_classes)
    else:
        pass

    model.train(train_images, train_labels)
    predictions, error_rate = model.inference(test_images, test_labels, args.num_test)
    print("\nError Rate: %.4f %%" % (error_rate*100))
