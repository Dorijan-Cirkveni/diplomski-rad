import os
import ast


def list_dependencies(folder_path):
    """
    Reads every Python file in the given folder and its subfolders
    and lists its dependencies (import statements).

    :param folder_path: Path to the folder to scan.
    :return: A dictionary with file paths as keys and a list of dependencies as values.
    """
    dependencies = {}

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                dependencies[file_path] = extract_dependencies(file_content)

    return dependencies


def extract_dependencies(file_content):
    """
    Extracts the import statements from a given Python file content.

    :param file_content: String content of a Python file.
    :return: A list of dependencies (imported modules).
    """
    dependencies = []
    try:
        tree = ast.parse(file_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for alias in node.names:
                    dependencies.append(f"{module}.{alias.name}" if module else alias.name)
    except SyntaxError:
        # If there's a syntax error in the file, skip it
        pass

    return dependencies


# Example usage
if __name__ == "__main__":
    folder_path = os.path.dirname(os.path.abspath(__file__))
    deps = list_dependencies(folder_path)
    for file, dependencies in deps.items():
        print(f"{file}:")
        for dep in dependencies:
            print(f"  - {dep}")
