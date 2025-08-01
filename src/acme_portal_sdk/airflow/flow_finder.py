import ast
import os
import sys
import traceback
from pprint import pp
from typing import Dict, List

from acme_portal_sdk.flow_finder import FlowDetails, FlowFinder

AirflowFlowDetails = FlowDetails


class AirflowFlowFinder(FlowFinder):
    """Scans Python code directories to identify Airflow DAGs by analyzing DAG instantiations, extracting metadata and organizing found DAGs into flat list."""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    class _DAGVisitor(ast.NodeVisitor):
        """AST visitor to find Airflow DAG definitions in Python code."""

        def __init__(self, module: str):
            self.dags = {}
            self.current_class = None
            self.current_function = None
            self.module = module

        def visit_ClassDef(self, node):
            old_class = self.current_class
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = old_class

        def visit_FunctionDef(self, node):
            """Visit a function definition node."""
            self.current_function = node.name
            # Look for decorators that might be @dag
            for decorator in node.decorator_list:
                if self._is_dag_decorator(decorator):
                    kwargs = self._extract_decorator_kwargs(decorator)
                    dag_id = kwargs.get("dag_id", node.name)
                    display_name = dag_id.replace("-", "_")

                    description = kwargs.get("description", "") or ast.get_docstring(
                        node
                    )

                    dag_key = f"{dag_id}_{id(node)}"

                    self.dags[dag_key] = {
                        "name": display_name,
                        "original_name": dag_id,
                        "description": description,
                        "obj_type": "function",
                        "obj_name": node.name,
                        "obj_parent_type": "module",
                        "obj_parent": self.module,
                        "module": self.module,
                        "id": dag_key,
                    }

                    if self.current_class:
                        self.dags[dag_key]["obj_parent"] = self.current_class
                        self.dags[dag_key]["obj_parent_type"] = "class"

                    print(
                        f"Found DAG: {display_name} (from decorated function {node.name})"
                    )

            self.generic_visit(node)
            self.current_function = None

        def visit_Assign(self, node):
            """Visit assignment nodes to find DAG instantiations."""
            # Look for DAG assignments like: my_dag = DAG(...)
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                if self._is_dag_instantiation(node.value):
                    dag_name = node.targets[0].id
                    kwargs = self._extract_dag_kwargs(node.value)

                    # Get DAG ID from kwargs or use variable name
                    dag_id = kwargs.get("dag_id", dag_name)
                    display_name = dag_id.replace("-", "_")

                    description = kwargs.get("description", "")

                    # Create a unique ID based on the DAG name and location
                    dag_key = f"{dag_id}_{id(node)}"

                    self.dags[dag_key] = {
                        "name": display_name,
                        "original_name": dag_id,
                        "description": description,
                        "obj_type": "dag",
                        "obj_name": dag_name,
                        "obj_parent_type": "module",
                        "obj_parent": self.module,
                        "module": self.module,
                        "id": dag_key,
                    }

                    if self.current_class:
                        self.dags[dag_key]["obj_parent"] = self.current_class
                        self.dags[dag_key]["obj_parent_type"] = "class"

                    # Debug output to help troubleshoot
                    print(f"Found DAG: {display_name} (from variable {dag_name})")

            self.generic_visit(node)

        def _is_dag_instantiation(self, node):
            """Check if a node is a DAG instantiation."""
            if isinstance(node, ast.Call):
                # Check for DAG() or airflow.DAG()
                if isinstance(node.func, ast.Name) and node.func.id == "DAG":
                    return True
                elif isinstance(node.func, ast.Attribute) and node.func.attr == "DAG":
                    return True
            return False

        def _is_dag_decorator(self, decorator):
            """Check if a decorator is a DAG decorator."""
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "dag"
            ):
                return True
            elif (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr == "dag"
            ):
                return True
            return False

        def _extract_dag_kwargs(self, node):
            """Extract keyword arguments from a DAG instantiation."""
            kwargs = {}
            if isinstance(node, ast.Call):
                for keyword in node.keywords:
                    if isinstance(keyword.value, ast.Constant):
                        kwargs[keyword.arg] = keyword.value.value
            return kwargs

        def _extract_decorator_kwargs(self, decorator):
            """Extract keyword arguments from a decorator."""
            kwargs = {}
            if isinstance(decorator, ast.Call):
                for keyword in decorator.keywords:
                    if isinstance(keyword.value, ast.Constant):
                        kwargs[keyword.arg] = keyword.value.value
            return kwargs

    def _scan_file(self, file_path: str) -> Dict[str, FlowDetails]:
        """Scan a single Python file for DAGs."""
        dags = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the file
            tree = ast.parse(content)
            module = os.path.splitext(os.path.basename(file_path))[0]
            visitor = self._DAGVisitor(module)
            visitor.visit(tree)

            # Process found DAGs
            for key, dag_data in visitor.dags.items():
                # Add file information
                dag_data["source_path"] = file_path
                dag_data["source_relative"] = os.path.relpath(
                    file_path, start=self.root_dir
                )
                dag_data["grouping"] = dag_data["source_relative"].split(os.sep)[
                    :-1
                ]  # Grouping by directory structure
                package_name = os.path.basename(self.root_dir)
                dag_data["import_path"] = (
                    f"{package_name}.{dag_data['source_relative'].replace(os.sep, '.').replace('.py', '')}"
                )
                dag_data = FlowDetails(**dag_data)
                # Add the DAG to the results
                dags[key] = dag_data

                print(f"Added DAG to results: {dag_data.name}")

        except Exception as e:
            print(f"Error scanning {file_path}: {str(e)}")
            traceback.print_exc(file=sys.stderr)

        return dags

    def _scan_directory(self, root_dir: str) -> Dict[str, FlowDetails]:
        """Recursively scan a directory for Python files with DAGs."""
        all_dags = {}

        print(f"Scanning directory: {root_dir}")

        try:
            for root, dirs, files in os.walk(root_dir):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        print(f"Examining file: {file_path}")
                        dags = self._scan_file(file_path)
                        if dags:
                            print(f"Found {len(dags)} DAGs in {file_path}")
                        all_dags.update(dags)
        except Exception as e:
            print(f"Error walking directory {root_dir}: {str(e)}")
            traceback.print_exc(file=sys.stderr)

        return all_dags

    def find_flows(self) -> List[FlowDetails]:
        return list(self._scan_directory(self.root_dir).values())


if __name__ == "__main__":
    finder = AirflowFlowFinder("examples/flows")
    pp(finder.find_flows())
