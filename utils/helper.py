import pickle

def save_file(fname, obj, mode='wb') :
    with open(fname, mode) as f :
        pickle.dump(obj, f)

def load_file(fname, mode='rb') :
    with open(fname, mode) as f :
        return pickle.load(f)
    
def _remove_punctuation_(string) :
    punc = r".,\/<>?;':\"[\]{}|!@#$%^&*()_+-="
    for i in punc :
        string = string.replace(i, "")
    return string

def _remove_numbers_(string) :
    numb = "1234567890"
    for i in numb :
        string = string.replace(i, "")
    return string

def cleaner(string) :
    tmp = string.lower()
    tmp = _remove_numbers_(tmp)
    tmp = _remove_punctuation_(tmp)
    return tmp
    
def main() :
    pass

if __name__ == "__main__" :
    main()
