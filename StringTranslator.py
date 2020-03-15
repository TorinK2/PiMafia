from ast import literal_eval


# Allows arrays to be translated to strings and then back to arrays
class StringTranslator:

    def __init__(self):  # Static function
        raise Exception("static")

    # Encodes array as a string
    @classmethod
    def encode(cls, array):
        return str(array)

    # Decodes string back to an array
    @classmethod
    def decode(cls, string):
        return literal_eval(string)


'''
You might ask why such a small class even needs to exist.
Originally, this class was much larger until I found these simple
and easy implementations. Now, it is in part legacy code and in
part a cleaner implementation that allows both GameClient and
GameServer to use the same functions.
Another question is why this class is static, as this is generally
not supported in Python. I have talked to professional developers about
whether static classes like this should exist, or whether I should simply
just list functions without a class structure. From this inquiry, I've found
that both implementations are equally acceptable, as both are simple to import
and work fine.
'''
