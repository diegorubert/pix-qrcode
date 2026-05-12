from pixqrcode.model.merchant_account import MerchantAccount
from pixqrcode.model.pix import Pix
from pixqrcode.utils.crc16 import crc16


class GenerateCode:
    def __init__(self):
        self.merchant = MerchantAccount()
        # IMPORTANTE: Isso não funcionava, pois o comprimento do email não é fixo.
        # Agora calculamos dinamicamente em generate.
        self.map_guis = {
            "mobile": "36",
            "cpf": "33",
            "cnpj": "36",
            "uuid": "58",
            "email": "45"  # <----- Não funciona
        }

    @classmethod
    def left_zero(cls, text: str):
        return str(len(text)).zfill(2)

    def generate(self, pix: Pix):
        if pix.method == "email":
            pass
        len_pix_key = len(pix.key)
        len_marchant = len('0014BR.GOV.BCB.PIX') + 2 + len(str(len_pix_key)) + len_pix_key
        return f"00020126{len_marchant}0014{self.merchant.globally_unique_identifier}01{len(pix.key)}{pix.key}520400005303986540" \
               f"{len(pix.amount.__str__())}{pix.amount.__str__()}5802{pix.country_code}59{self.left_zero(pix.name)}" \
               f"{pix.name}60{self.left_zero(pix.city)}{pix.city}" \
               f"62{str(len(pix.reference_label) + 4).zfill(2)}05{self.left_zero(pix.reference_label)}" \
               f"{pix.reference_label}6304"

    @classmethod
    def crc16code(cls, query: str) -> str:
        return hex(crc16(query.encode())).__str__()

    def format_code(self, pix: Pix):
        hash_payment = self.generate(pix)
        return f"{hash_payment}{self.crc16code(hash_payment).upper()[2:]}".strip()
