import cPickle as pickle


def save_to_pkl(pth, **vars):
    with open(pth, 'w') as f:
        pickle.dump(vars, f)
    print 'saved to {}'.format(pth)


def load_from_pkl(pth):
    with open(pth, 'r') as f:
        return pickle.load(f)
