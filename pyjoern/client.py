import os
import re
import logging
from typing import Set
from pathlib import Path

from cpgqls_client import CPGQLSClient, import_code_query
import networkx as nx

l = logging.getLogger(__name__)


class JoernClient:
    def __init__(self, target_file, ip="localhost", port=9000, bin_name=None):
        self.ip = ip
        self.port = port
        self.target_file = Path(target_file).absolute()
        self.bin_name = bin_name or ""

        # connect and import target file
        self.client = CPGQLSClient(f"{ip}:{port}")
        self.client.execute(import_code_query(f"{self.target_file}", f"{os.path.basename(self.target_file)}"))
        self.functions: Set[str] = self._get_functions_with_code()

        # cache
        self.cfg_cache = {}

    #
    # Public API
    #
    
    def function_line_numbers(self):
        out = self._exec_list_cmd("cpg.method.filter(node => node.lineNumber!=None&&node.lineNumberEnd!=None).map(node => (node.name, node.lineNumber.last, node.lineNumberEnd.last)).l")
        if not out:
            return {}

        if not isinstance(out, (list, tuple)):
            return {}

        line_nums_by_func = {}
        for data in out:
            if not isinstance(data, (list, tuple)) or len(data) != 3:
                continue

            fn, ln_start, ln_end = data
            if fn not in self.functions:
                continue

            line_nums_by_func[fn] = (ln_start, ln_end)

        return line_nums_by_func

    def function_headers(self):
        headers = {}
        for func in self.functions:
            out = self._exec_list_cmd(f'cpg.method.filter(_.name=="{func}").code.l')
            if not out:
                continue

            if not isinstance(out, (list, tuple)):
                continue

            headers[func] = out[0]

        return headers

    def function_code(self, full_funcname):
        out = self._exec_list_cmd(f'cpg.method.filter(_.fullName=="{full_funcname}").code.l')
        if not out:
            return None

        if not isinstance(out, (list, tuple)):
            return 
  
        return out[0]
    
    def functions_with_gotos(self):
        out1 = self._exec_list_cmd(f'cpg.goto.method.name.l')
        if not out1:
            return []

        if isinstance(out1, (list, tuple)) and len(out1) > 0:
            return out1

        return []
        
    def functions_with_switches(self):
        out1 = self._exec_list_cmd(f'cpg.switchBlock.method.name.l')
        if not out1:
            return []

        if isinstance(out1, (list, tuple)) and len(out1) > 0:
            return out1

        return []

    def get_func_cfg(self, func_name):
        if func_name in self.cfg_cache:
            return self.cfg_cache[func_name]

        cfg = self._dump_func_cfg(func_name)
        self.cfg_cache[func_name] = cfg

        return cfg

    def get_func_loc(self, func_name):
        """
        Gets a functions lines of code (loc) count.
        """
        if func_name not in self.functions:
            return None

        out1 = self._exec_list_cmd(f'cpg.method.filter(_.name=="{func_name}").lineNumber.l')
        if out1 is None:
            return None

        out2 = self._exec_list_cmd(f'cpg.method.filter(_.name=="{func_name}").lineNumberEnd.l')
        if out2 is None:
            return None

        start_line = out1[-1] if not isinstance(out1, int) else out1
        end_line = out2[-1] if not isinstance(out2, int) else out2

        try:
            val = int(end_line) - int(start_line)
        except Exception:
            return None
        return val
    
    def function_ternary_counts(self):
        count = {}
        for func_name in self.functions:
            out = self._exec_int_cmd(f'cpg.method.filter(_.name=="{func_name}").call.filter(_.name=="<operator>.conditional").filter(_.code.contains("__builtin_unreachable")==false).size')
            if out is None:
                continue
            count[func_name] = out 

        return count
            

    def count_gotos(self, func_name):
        if func_name not in self.functions:
            return None

        out = self._exec_int_cmd(f'cpg.method.filter(_.name=="{func_name}").goto.size')
        if out is None:
            return None

        return out

    def count_if_levels(self, func_name):
        """
        Returns the max of if-nesting level

        """
        out = self._exec_list_cmd(
            f'cpg.method.filter(_.name=="{func_name}").controlStructure.controlStructureType("IF").depth(_.isControlStructure).l'
        )
        if out is None or (isinstance(out, (list, tuple)) and len(out) == 0):
            return None

        # if_count = out if isinstance(out, int) else sum(out) // len(out)
        if_count = out if isinstance(out, int) else max(out)
        return if_count

    def func_calls_in_func(self, func_name):
        out = self._exec_list_cmd(
            f'cpg.method.filter(_.name=="{func_name}").call.name.l'
        )
        if out is None:
            return None

        out = [out] if isinstance(out, str) else out
        # good_funcs = self._filter_blacklisted(out)
        # return good_funcs
        return out
    
    def func_calls_in_func_with_fullname(self, func_name):
        out = self._exec_list_cmd(
            f'cpg.method.filter(_.name=="{func_name}").call.methodFullName.l'
        )
        if out is None:
            return None

        out = [out] if isinstance(out, str) else out
        # good_funcs = self._filter_blacklisted(out)
        # return good_funcs
        return out
    
    def get_control_structure_conditions(self, func_name):
        if func_name not in self.functions:
            return None

        out = self._exec_list_cmd(
            f'cpg.method.filter(_.name=="{func_name}").controlStructure.condition.code.l'
        )
        if not isinstance(out, (tuple, list)):
            return None

        return list(out)

    def get_filename(self, func_name):
        out = self._exec_list_cmd(
            f'cpg.method.filter(_.name=="{func_name}").filename.l'
        )
        if out is None:
            return None
        return out[0]
    
    def get_full_funcname(self, func_name):
        out = self._exec_list_cmd(
            f'cpg.method.filter(_.name=="{func_name}").fullName.l'
        )
        if out is None:
            return None
        return out[0]

    def get_function_details(self, funcname):
        out = self._exec_list_cmd(
            f'cpg.method.filter(_.name=="{funcname}").filter(node => node.lineNumber!=None&&node.lineNumberEnd!=None&&node.body.typeFullName!="<empty>").map(x => (x.fullName, x.filename, x.lineNumber.getOrElse(None), x.lineNumberEnd.getOrElse(None), x.signature, x.name, x.signature)).l'
        )
        if not isinstance(out, (tuple, list)):
            function_details = []
            return function_details
        out = out if isinstance(out, tuple) and isinstance(out[0], tuple) else (out,)
        
        function_details = []
        
        for fullfuncname, filename, start_line, end_line, func_return_type, name, signature in out:
            if start_line is not None and end_line is not None: 
                function_details.append({
                    'fullfuncname': fullfuncname, 
                    'filename': filename, 
                    'start_line': start_line, 
                    'end_line': end_line,
                    'func_return_type': func_return_type,
                    'name': name, # We need this fied cuz we need to compare it with fullfuncname
                    'signature': signature # 
                })

        return function_details

    def func_arguments(self, funcname):
        try:
            out = self._exec_list_cmd(
                f'cpg.method.filter(_.name=="{funcname}").flatMap(m => m.parameter.map(x => (m.filename, x.name, x.code, x.lineNumber.getOrElse(None), x.columnNumber.getOrElse(None)))).l'
            )
            if not out:
                return {}
            out = out if isinstance(out, tuple) and isinstance(out[0], tuple) else (out,)
                
            argnames_list = {}
            for filename, argname, code, line, col in out:
                if line is None:
                    continue
                if filename not in argnames_list:
                    argnames_list[filename] = {}
                argnames_list[filename][argname] = {'code': code, 'line': line, 'column': col}
            return argnames_list
        
        # TODO: why do I get extra args with no linenumber?
        except Exception as e:
            l.warning(f"Error occurred doing JOERN eval for {funcname} while collecting args because {e}")
            return {}
        
    def isMacro(self,fname):
        out = self.client.execute(
            f'cpg.method.filter(node => node.lineNumber!=None&&node.lineNumberEnd!=None&&node.body.typeFullName!="<empty>").filter(_.name=="{fname}").where(_.body.typeFullName("ANY")).size'
        )
        out = int(out['stdout'].split("Int = ")[1])
        if out != 0:
            return True
        else:
            return False

    def global_variables(self):
        out = self._exec_list_cmd(
        f'cpg.local.where(_.method.filter(_.name=="<global>")).map(x=> (x.name, x.lineNumber.getOrElse(None), x.columnNumber.getOrElse(None))).l'
        )

        if not out:
            return {}
        out = out if isinstance(out, tuple) and isinstance(out[0], tuple) else (out,)
        
        vars = {varname: {'line': line, 'column': col} for varname, line, col in out}
        return vars

    def local_variables(self, funcname):
        out = self._exec_list_cmd(
            f'cpg.method.filter(_.name=="{funcname}").flatMap(m => m.local.map(x => (m.filename, x.name, x.lineNumber.getOrElse(None), x.columnNumber.getOrElse(None)))).l'
        )

        if not out:
            return {}
        out = out if isinstance(out, tuple) and isinstance(out[0], tuple) else (out,)
        
        vars = {}
        for filename, varname, line, col in out:
            if line is None:
                continue
            if filename not in vars:
                vars[filename] = {}
            vars[filename][varname] = {'line': line, 'column': col}

        return vars
    
    # TODO: update this!
    def graph_edges_with_properties(self, code, property):
        out = self._list_parsing_regex(
            f'cpg.graph.E.map(edge=>(edge.inNode.id, edge.outNode.id, edge.label, edge.propertiesMap.get("{property}"))).l')
        
        if out is None:
            return []
        return out
    
    def graph_nodes(self, code):
        out = self.client.execute(
            f'cpg.graph.V.map(node=>node).toJson'
        )
        res_out = out['stdout'].split('String = ')[-1]
        return eval(res_out)

    #
    # Private Helpers
    #
    
    # TODO: for future we should reduce number of queries we are running for the speed. 
    # consider fetching multiple info in one query. 
    # for example: cpg.method.filter(node => node.lineNumber!=None&&node.lineNumberEnd!=None&&node.lineNumber!=node.lineNumberEnd).map(node=>(node.name, node.fullName, node.filename)).l
    
    def _get_functions_with_code(self):
        out = self._exec_list_cmd(
            'cpg.method.filter(node => node.lineNumber!=None&&node.lineNumberEnd!=None&&node.body.typeFullName!="<empty>").name.l' # Filter all the declarations
        )
        if not isinstance(out, (tuple, list)):
            return []

        out = list(out)
        # return set(self._filter_blacklisted(out))
        return set(out)

    @staticmethod
    def _filter_blacklisted(strings):
        blacklist = [
            "<", "+", "*", "(", ">", "JUMPOUT", "__builtin_unreachable"
        ]
        good_strings = []
        for string in strings:
            if not any(string.startswith(b) for b in blacklist):
                good_strings.append(string)

        return good_strings

    def _exec_list_cmd(self, raw_command):
        res = self.client.execute(f"{raw_command}")
        tuple_str = self._get_str_tuple(res, cmd=raw_command)
        return tuple_str

    def _exec_int_cmd(self, raw_command):
        res = self.client.execute(f"{raw_command}")
        int_val = self._get_str_int(res, cmd=raw_command)
        if int_val is None or not isinstance(int_val, int):
            return None

        return int_val
    
    def _get_str_int(self, req_res, cmd=None):
        if 'stdout' not in req_res:
            return None

        out = None
        try:
            raw_out = req_res['stdout']
            out = int(raw_out, 10)
        except Exception as e:
            l.warning(f"Error occurred doing JOERN eval for {self.bin_name} on {cmd} because {e}")

        return out

    def _get_str_tuple(self, req_res, cmd=None):
        if 'stdout' not in req_res:
            return None
        
        try:
            raw_out = req_res['stdout'].split("= List(")[-1]
            str_tuple = eval("(" + raw_out)
        except Exception as e:
            l.warning(f"Error occurred doing JOERN eval for {self.bin_name} on {cmd} because {e}")
            return None

        if type(str_tuple) == str:
            str_tuple = [str_tuple]

        return str_tuple

    def _dump_func_cfg(self, func_name):
        str_tuple = self._exec_list_cmd(f'cpg.method.filter(_.name=="{func_name}").dotCfg.l')
        try:
            graph = nx.nx_agraph.from_agraph(pg.AGraph(str_tuple[-1]))
        except Exception as e:
            l.warning(f"Error getting CFG from JOERN for {self.bin_name} on {func_name} as {e}")
            graph = None

        return graph

    def _list_parsing_regex(self, raw_command):
        res = self.client.execute(f"{raw_command}")
        if 'stdout' not in res:
            return None
        
        result_list = []
        raw_out = res['stdout'].split('] = List')[-1]

        # TODO set how many elements you need in each tuple for pattern_gen
        pattern = r'\(\s*(\d+L)\s*,\s*(\d+L)\s*,\s*"(.*?)"\s*,\s*(.*?)\s*\)'
        regex = re.compile(pattern)
        matches = regex.finditer(raw_out)
        for m in matches:
            elements = m.groups()
            result_list.append([(elem) for elem in elements])
        return result_list
        
      