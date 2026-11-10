from pixqrcode.model.merchant_account import MerchantAccount
from pixqrcode.model.pix import Pix
from pixqrcode.utils.crc16 import crc16


class GenerateCode:
    def __init__(self):
        self.merchant = MerchantAccount()

    @classmethod
    def left_zero(cls, text: str):
        return str(len(text)).zfill(2)

    @classmethod
    def tlv(cls, tag: str, value: str) -> str:
        """
    Monta um campo EMV: ID (2 dígitos) + tamanho (sempre 2 dígitos) + valor
        """
        value = str(value)
        if len(value) > 99:
            raise ValueError("Campo {0} excede 99 caracteres: {1}".format(tag, value))
        return f"{tag}{cls.left_zero(value)}{value}"

    def generate(self, pix: Pix):
        merchant_account = self.tlv("00", self.merchant.globally_unique_identifier) + self.tlv("01", pix.key)
        additional_data = self.tlv("05", pix.reference_label)
        return (
            self.tlv("00", "01")
            + self.tlv(self.merchant.merchant_account_information, merchant_account)
            + self.tlv("52", pix.merchant_category_code)
            + self.tlv("53", pix.transaction_currency)
            + self.tlv("54", pix.amount)
            + self.tlv("58", pix.country_code)
            + self.tlv("59", pix.name)
            + self.tlv("60", pix.city)
            + self.tlv("62", additional_data)
            + "6304"
        )

    @classmethod
    def crc16code(cls, query: str) -> str:
        # O CRC tem tamanho fixo: sempre 4 dígitos hexadecimais, com zeros à esquerda
        return f"{crc16(query.encode()):04X}"

    def format_code(self, pix: Pix):
        hash_payment = self.generate(pix)
        return f"{hash_payment}{self.crc16code(hash_payment)}".strip()
