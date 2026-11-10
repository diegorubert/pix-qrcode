import re
import unicodedata


class FormatValues:
    @staticmethod
    def remove_accents(text: str):
        # "MUNHÕES" -> "MUNHOES", "Ç" -> "C" (em vez de apagar a letra)
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

    @staticmethod
    def texts(text: str):
        text = re.sub(r'[^0-9a-zA-Z\s]+', '', FormatValues.remove_accents(text))
        return " ".join(text.split())

    @staticmethod
    def truncate(text: str, max_len: int):
        return text[:max_len].rstrip()

    @staticmethod
    def amount(amount: str):
        value_base = re.sub(r'[^0-9]', '', amount).upper()
        return '{:.2f}'.format((int(value_base) / 100)).__str__()

    @staticmethod
    def mobile(mobile: str):
        return re.sub(r'[^0-9]', '', mobile).upper()

    @staticmethod
    def texts_no_space(text: str):
        return re.sub(r'[^0-9a-zA-Z]+', '', FormatValues.remove_accents(text))
