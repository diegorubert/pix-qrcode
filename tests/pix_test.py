import os
import unittest

from pixqrcode import PixQrCode, PixError
from pixqrcode.service.generate_code import GenerateCode


def parse_tlv(payload: str) -> dict:
    """Parser EMV estrito: falha se algum tamanho declarado não bater."""
    fields, i = {}, 0
    while i < len(payload):
        tag, size = payload[i:i + 2], int(payload[i + 2:i + 4])
        value = payload[i + 4:i + 4 + size]
        if len(value) != size:
            raise ValueError("campo {0} declara {1} mas tem {2}".format(tag, size, len(value)))
        fields[tag] = value
        i += 4 + size
    return fields


class PixTestCase(unittest.TestCase):

    def test_crc_manual_bacen(self):
        # Exemplo de QR code estático do Manual do BR Code
        body = "00020126580014br.gov.bcb.pix0136123e4567-e12b-12d1-a456-426655440000" \
               "5204000053039865802BR5913Fulano de Tal6008BRASILIA62070503***6304"
        self.assertEqual(GenerateCode.crc16code(body), "1D3D")

    def test_crc_keeps_leading_zero(self):
        pix = PixQrCode(
            name="Joao Carlos",
            key="(85) 98695-9807",
            amount="5900",
            city="Sao Paulo",
        )
        code = pix.generate_code()
        # CRC 0x0F18: antes era gerado como "F18" (3 dígitos), invalidando o QR code
        self.assertTrue(code.endswith("63040F18"))
        self.assertEqual(parse_tlv(code)["63"], "0F18")

    def test_long_name_truncated(self):
        pix = PixQrCode(
            name="Maria Eduarda Nunes Rocha da Silva",
            key="(85) 98695-9807",
            amount="10000",
            city="Campo Grande do Sul Mato",
            reference_label="REFERENCIA MUITO LONGA PARA O CAMPO TXID",
        )
        fields = parse_tlv(pix.generate_code())
        self.assertEqual(fields["59"], "Maria Eduarda Nunes Rocha")
        self.assertLessEqual(len(fields["59"]), 25)
        self.assertLessEqual(len(fields["60"]), 15)
        self.assertLessEqual(len(parse_tlv(fields["62"])["05"]), 25)

    def test_accents_transliterated(self):
        pix = PixQrCode(
            name="Bárbara Munhões  Conceição",
            key="(85) 98695-9807",
            amount="10000",
            city="São Paulo",
        )
        fields = parse_tlv(pix.generate_code())
        self.assertEqual(fields["59"], "Barbara Munhoes Conceicao")
        self.assertEqual(fields["60"], "Sao Paulo")

    def test_validation_fail(self):
        key = "123"
        pix = PixQrCode(
            name="Joao Carlos",
            key=key,
            amount="255.00",
            city="São Paulo",
        )
        try:
            pix.is_valid()
        except Exception as e:
            self.assertEqual(type(e), PixError)
            self.assertEqual(str(e), "Chave pix inválida {0}".format(key))

    def test_validation_success(self):
        pix = PixQrCode(
            name="Joao Carlos",
            key="(85) 98695-9807",
            amount="255.00",
            city="São Paulo",
        )
        self.assertTrue(pix.is_valid())

    def test_generate_code(self):
        pix = PixQrCode(
            name="Joao Carlos",
            key="488.617.308-08",
            amount="255.00",
            city="Santa Branca",
        )
        self.assertIsNotNone(pix.generate_code())

    def test_export_base64(self):
        pix = PixQrCode(
            name="Joao Carlos",
            key="(85) 98695-9807",
            amount="255.00",
            city="São Paulo",
        )
        self.assertIsNotNone(pix.export_base64())

    def test_save_file(self):
        pix = PixQrCode(
            name="Joao Carlos",
            key="00834420228",
            amount="255.00",
            city="São Paulo",
        )
        self.assertTrue(pix.save_qrcode("pix-joao"))
        self.assertTrue(os.path.exists("./pix-joao.png"))
        os.remove("./pix-joao.png")

    def test_valid_keys(self):
        keys_list = [
            "(85) 98695-9807",
            "85986959807"
            "carolina-nogueira85@econe.com.br",
            "318.727.125-17",
            "31872712517",
            "11.110.312/0001-74",
            "11110312000174",
            "1c33467b-be1b-4db6-aa18-296849cf85bb"
        ]

        for key in keys_list:
            pix = PixQrCode(
                name="Joao Carlos",
                key=key,
                amount="255.00",
                city="São Paulo",
            )
            self.assertTrue(pix.is_valid())


if __name__ == '__main__':
    unittest.main()
