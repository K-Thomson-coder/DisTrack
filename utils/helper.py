import pickle

def save_file(fname, obj, mode='wb') :
    with open(fname, mode) as f :
        pickle.dump(obj, f)

def load_file(fname, mode='rb') :
    with open(fname, mode) as f :
        return pickle.load(f)
    
def main() :
    pass

if __name__ == "__main__" :
    main()
