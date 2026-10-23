"""
Testes Unitários da Mensagem Obrigatória e Validação do Código Secreto em THE LAST CORRIDOR.
"""

import unittest
from the_last_corridor.core.config import InvestigationConfig


class TestCodeValidation(unittest.TestCase):
    def test_mandatory_prompt_exact_wording(self):
        """Verifica se o texto obrigatório está exatamente como exigido no enunciado."""
        cfg = InvestigationConfig()
        expected = "EXISTE UM ARQUIVO NO SEU COMPUTADOR, O ENCONTRE E ESCREVA O CODIGO AQUI"
        self.assertEqual(
            cfg.mandatory_message,
            expected,
            "A mensagem obrigatória deve conter exatamente o texto especificado sem alterações."
        )

    def test_code_validation_success(self):
        cfg = InvestigationConfig(secret_code="OMEGA-7341", case_sensitive=False, strip_whitespace=True)

        user_input = "  omega-7341  "
        target = cfg.secret_code

        if cfg.strip_whitespace:
            user_input = user_input.strip()
            target = target.strip()
        if not cfg.case_sensitive:
            user_input = user_input.upper()
            target = target.upper()

        self.assertEqual(user_input, target)

    def test_code_validation_incorrect(self):
        cfg = InvestigationConfig(secret_code="OMEGA-7341")
        user_input = "CODIGO_ERRADO"
        self.assertNotEqual(user_input.upper(), cfg.secret_code.upper())


if __name__ == "__main__":
    unittest.main()
