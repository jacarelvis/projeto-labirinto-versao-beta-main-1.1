"""
Testes Unitários do Sistema de Arquivos Virtual de THE LAST CORRIDOR.
"""

import unittest
from the_last_corridor.core.config import GameConfig
from the_last_corridor.desktop.virtual_filesystem import VirtualFileSystem


class TestVirtualFileSystem(unittest.TestCase):
    def setUp(self):
        self.default_tree = GameConfig.get_default_filesystem_tree()
        self.vfs = VirtualFileSystem(self.default_tree)

    def test_root_exists(self):
        root = self.vfs.get_node_by_path("root")
        self.assertIsNotNone(root)
        self.assertEqual(root.name, "root")

    def test_navigate_to_subfolders(self):
        pessoal = self.vfs.get_node_by_path("Meus Documentos/Pessoal")
        self.assertIsNotNone(pessoal)
        self.assertEqual(pessoal.name, "Pessoal")
        self.assertEqual(pessoal.type, "folder")

    def test_read_file_content(self):
        content = self.vfs.get_file_content("Desktop/LEIA-ME.txt")
        self.assertIsNotNone(content)
        self.assertIn("SE VOCE ESTA LENDO ISTO", content)

    def test_secret_code_file_exists(self):
        content = self.vfs.get_file_content("Arquivos/sistema/acesso_restrito.txt")
        self.assertIsNotNone(content)
        self.assertIn("Venlafaxina", content)

    def test_nonexistent_file_returns_none(self):
        content = self.vfs.get_file_content("PastaInexistente/fantasma.txt")
        self.assertIsNone(content)

    def test_list_children(self):
        children = self.vfs.list_children("Desktop")
        names = [name for name, ntype in children]
        self.assertIn("LEIA-ME.txt", names)
        self.assertIn("notas_antigas.txt", names)


if __name__ == "__main__":
    unittest.main()
