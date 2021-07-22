import ast
import copy
from typing import List

from .utils import escape
from .out import SimplificationResult
import fastpy.constants as constants

class Context:
    def __init__ (self, module: ast.Module, is_main: bool):
        self.module: ast.Module = module
        self.is_main = is_main

        self.solved = False
        self.output = None

        self.current_local_number = 0
        self.includes = []
        self.out_statements: List [SimplificationResult] = []

        self._builtins_imported = False
    def solve (self):
        if self.solved: return self.output


        for statement in self.module.body:
            self.out_statements.append (self.simplify (statement))

        includes_blob = "\n".join (f"#include <{include}>" for include in self.includes)

        out_statements_blob = '\n'.join (f"{constants.INDENT}{out_statement}" for out_statement in self.out_statements)
        assert self.is_main
        self.output = f"{includes_blob}\n" \
                      f"\n" \
                      f"int main () {{\n" \
                      f"{out_statements_blob}\n" \
                      f"}}"

        self.solved = True

        return self.output
    def simplify (self, node: ast.AST) -> SimplificationResult:
        def check (_type: type): return isinstance (node, _type)
        node_type = type (node)

        if check (ast.expr): return self._simplify_expr (node)
        elif check (ast.stmt):
            return self._simplify_stmt (node)
        if check (ast.mod):
            if check (ast.Module):
                raise Exception ("make a new context to parse a module!")
            else: raise Exception (f"unknown module subtype {node_type}")
        else: raise Exception (f"unknown node type {node_type}")
    def _simplify_stmt (self, node: ast.stmt) -> SimplificationResult:
        def check (_type: type): return isinstance (node, _type)
        node_type = type (node)


        if isinstance (node, ast.Expr): return self._simplify_expr (node.value)
        if check (ast.FunctionDef):
            print ("ast function def")
        else:
            raise Exception (f"unknown statement subtype {node_type}")
    def _simplify_expr (self, node: ast.expr) -> SimplificationResult:
        def check (_type: type): return isinstance (node, _type)
        node_type = type (node)

        print (f"expr {node} {type (node)}")
        if check (ast.Call):
            print ("ast call")
            node: ast.Call

            src_func_name = self._simplify_expr (node.func)
            if src_func_name not in constants.IMPLEMENTED_BUILTINS: raise Exception (
                f"unimplemented builtin {src_func_name}")
            self._add_include (constants.PATH_TO_BUILTINS_H)
            func_name = constants.JOIN_NAMESPACE (constants.BUILTINS_NAMESPACE, src_func_name)

            args_and_kwargs_solution = {}
            src_func_desc = constants.IMPLEMENTED_BUILTINS [src_func_name]
            mutable_src_signature = copy.deepcopy (src_func_desc ["signature"])

            for dst_kwarg in node.keywords:
                dst_kwarg: ast.keyword
                assert dst_kwarg.arg
                if dst_kwarg.arg not in [src_kwarg ["name"] for src_kwarg in mutable_src_signature ["kwargs"]]:
                    raise Exception (f"unrecognized kwarg {dst_kwarg.arg} = {dst_kwarg.value}")
                if dst_kwarg.arg in [src_arg ["name"] for src_arg in mutable_src_signature ["args"]]:
                    print ("found match for keyword in arguments")
                    matching_arg = mutable_src_signature ["args"] [[src_arg ["name"] for src_arg in mutable_src_signature ["args"]].index (dst_kwarg.arg)]
                    args_and_kwargs_solution [matching_arg ["name"]] = self._process_constant_value (dst_kwarg.value)
                    del matching_arg
                    continue
                matching_kwarg = mutable_src_signature ["kwargs"] [[src_kwarg ["name"] for src_kwarg in mutable_src_signature ["kwargs"]].index (dst_kwarg.arg)]
                args_and_kwargs_solution [matching_kwarg ["name"]] = self._process_constant_value (dst_kwarg.value.value)

            src_args = mutable_src_signature ["args"]
            dst_args = node.args
            if len (dst_args) < len (src_args): raise Exception (f"{len (dst_args)} args given when {'at least ' if src_args [-1] ['starred'] else ''}{len (src_args)} needed")
            if len (src_args) == 0:
                if len (dst_args) > 0: raise Exception (f"{len (dst_args)} args given when none in signature")
            else:
                if src_args [-1] ["starred"]:
                    if len (src_args) < len (src_args): raise Exception (f"need at least {len (src_args)} args")
                    for arg_index, src_arg in enumerate (src_args):
                        print (f"processing arg {src_arg} (#{arg_index})")
                        arg_solution = self._process_tuple_of_constants (tuple (dst_args [arg_index:])) if src_arg ["starred"] else self._process_constant_value (dst_args [arg_index])
                        args_and_kwargs_solution [src_arg ["name"]] = arg_solution


            for dst_item in mutable_src_signature ["dst_ordering"]:
                if dst_item in args_and_kwargs_solution: continue
                if dst_item not in [src_kwarg ["name"] for src_kwarg in mutable_src_signature ["kwargs"]]:
                    raise Exception (f"missing arg {dst_item}")
                matching_kwarg = mutable_src_signature ["kwargs"] [[src_kwarg ["name"] for src_kwarg in mutable_src_signature ["kwargs"]].index (dst_item)]
                if "default" not in matching_kwarg:
                    raise Exception (f"missing kwarg {dst_item} with no default")
                args_and_kwargs_solution [dst_item] = self._process_constant_value (matching_kwarg ["default"])

            print (args_and_kwargs_solution)

            ordered_solution = [args_and_kwargs_solution [dst_item] for dst_item in mutable_src_signature ["dst_ordering"]]

            return f"{func_name} ({', '.join (ordered_solution)});"
        elif check (ast.Constant):
            node: ast.Constant
            in_value = node.value
            return self._process_constant_value (in_value)
        elif check (ast.Name):
            node: ast.Name
            return node.id
        else:
            if hasattr (node, "value") and isinstance (getattr (node, "value"), ast.expr): return self._simplify_expr (node.value)
            raise Exception (f"unknown expression subtype {node_type}")
    def _process_tuple_of_constants (self, tuple_of_constants: tuple):
        self._add_include ("tuple")
        types_list = []
        out_values_list = []
        for constant in tuple_of_constants:
            assert type (constant) == ast.Constant, "no support for non constants in tuples yet"
            constant: ast.Constant
            value = constant.value
            if type (value) not in constants.TYPES_MAPPING: raise Exception (
                f"unknown constant type {type (value)}")
            self._add_include (constants.PATH_TO_TYPES_H)
            constant_out_type = constants.WRAP_CLASS (
                constants.JOIN_NAMESPACE (constants.TYPES_NAMESPACE, constants.TYPES_MAPPING [type (value)]))
            types_list.append (constant_out_type)
            print (f"out type {constant_out_type}")

            out_value = escape (value)
            out_values_list.append (out_value)
        tuple_of_constants_result = f"std::tuple <{', '.join (types_list)}> ({', '.join (out_values_list)})"
        print (tuple_of_constants_result)
        return tuple_of_constants_result
    def _process_constant_value (self, value):
        if type (value) not in constants.TYPES_MAPPING: raise Exception (f"unknown constant type {type (value)}")
        self._add_include (constants.PATH_TO_TYPES_H)
        constant_out_type = constants.WRAP_CLASS (
            constants.JOIN_NAMESPACE (constants.TYPES_NAMESPACE, constants.TYPES_MAPPING [type (value)]))
        print (f"out type {constant_out_type}")
        return f"{constant_out_type} ({escape (value)})"
    def _add_include (self, new_include: str):
        if new_include not in self.includes: self.includes.append (new_include)
    def _next_local_name (self) -> str:
        new_local_name = f"__fastpy_local_{self.current_local_number}"
        self.current_local_number += 1
        return new_local_name
    def _insert_statement (self, raw_statement: SimplificationResult) -> None:
        self.out_statements.append (raw_statement)
    def _new_local (self, base_type: str, init_arg: str) -> str:
        new_local_name = self._next_local_name ()
        wrapped_constant_type = constants.WRAP_CLASS (base_type)
        self._insert_statement (f"{wrapped_constant_type} {new_local_name} = {base_type} ({init_arg});")
        return new_local_name
