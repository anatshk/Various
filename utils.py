import pickle


def save_to_pkl(pth, **vars):
    with open(pth, 'wb') as f:
        pickle.dump(vars, f)
    print('saved to {}'.format(pth))


def load_from_pkl(pth):
    with open(pth, 'rb') as f:
        return pickle.load(f)
