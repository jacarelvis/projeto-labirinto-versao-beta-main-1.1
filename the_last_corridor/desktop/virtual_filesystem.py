"""
Sistema de Arquivos Virtual de THE LAST CORRIDOR.
Estrutura de dados em árvore totalmente isolada e em memória, simulando o disco rígido do computador fictício.
"""

from typing import Dict, List, Optional, Any, Tuple


class VirtualNode:
    def __init__(self, name: str, node_type: str = "folder", content: str = ""):
        self.name = name
        self.type = node_type  # "folder" or "file"
        self.content = content  # Para arquivos .txt
        self.children: Dict[str, "VirtualNode"] = {}
        self.parent: Optional["VirtualNode"] = None

    def add_child(self, child: "VirtualNode"):
        child.parent = self
        self.children[child.name] = child

    def get_path(self) -> str:
        """Retorna o caminho virtual completo (ex: Meus Documentos/Pessoal)."""
        parts = []
        curr = self
        while curr and curr.name != "root":
            parts.append(curr.name)
            curr = curr.parent
        return "/".join(reversed(parts))


class VirtualFileSystem:
    def __init__(self, tree_dict: Dict[str, Any]):
        self.root = self._build_tree(tree_dict)

    def _build_tree(self, data: Dict[str, Any], name: str = "root") -> VirtualNode:
        node_type = data.get("type", "folder")
        content = data.get("content", "")
        node = VirtualNode(name=name, node_type=node_type, content=content)

        if node_type == "folder" and "children" in data:
            for child_name, child_data in data["children"].items():
                child_node = self._build_tree(child_data, name=child_name)
                node.add_child(child_node)

        return node

    def get_node_by_path(self, path_str: str) -> Optional[VirtualNode]:
        """Localiza um nó por seu caminho relativo (ex: 'Meus Documentos/Relatorios')."""
        clean_path = path_str.strip("/").strip()
        if not clean_path or clean_path == "root":
            return self.root

        parts = clean_path.split("/")
        curr = self.root

        for part in parts:
            if part in curr.children:
                curr = curr.children[part]
            else:
                return None
        return curr

    def list_children(self, path_str: str) -> List[Tuple[str, str]]:
        """Retorna lista de tuplas (nome, tipo) para a pasta indicada."""
        node = self.get_node_by_path(path_str)
        if node and node.type == "folder":
            return [(name, child.type) for name, child in sorted(node.children.items())]
        return []

    def get_file_content(self, path_str: str) -> Optional[str]:
        """Lê o conteúdo textual de um arquivo fictício."""
        node = self.get_node_by_path(path_str)
        if node and node.type == "file":
            return node.content
        return None
