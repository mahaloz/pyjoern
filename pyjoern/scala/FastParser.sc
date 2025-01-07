import scala.util.{Try, Success, Failure}

def toJson_pp(query: Any, indentLevel: Int = 0): String = {
  val indent = " " * (indentLevel * 4) // 4 spaces for each indent level
  query match {
    case m: Map[_, _] =>
      m.asInstanceOf[Map[String, Any]].map {
        case (k, v) => s"""$indent    "$k": ${toJson_pp(v, indentLevel + 1)}"""
      }.mkString("{\n", ",\n", s"\n$indent}")
    case t: (String, Any) => s"""$indent"$${t._1}": ${toJson_pp(t._2, indentLevel)}"""
    case ss: Seq[_] => ss.map(toJson_pp(_, indentLevel + 1)).mkString("[\n", ",\n", s"\n$indent]")
    case s: String => "\"" + escapeString(s) + "\""
    case null => "null"
    case other => other.toString
  }
}

def escapeString(str: String): String = {
  str
    .replaceAllLiterally("\\", "\\\\") // Escape backslashes
    .replaceAllLiterally("\n", "\\n")  // Escape newlines
    .replaceAllLiterally("\r", "\\r")  // Escape carriage returns
    .replaceAllLiterally("\t", "\\t")  // Escape tabs
    .replaceAllLiterally("\"", "\\\"") // Escape double quotes
}

@main def exec(target_dir: String, no_metadata: Boolean = false, no_cfg: Boolean = false, no_ddg: Boolean = false, no_ast: Boolean = false) = {
  val cpg = importCode(target_dir)

  val function_names = cpg.method
    .filter(node => node.lineNumber.isDefined && node.lineNumberEnd.isDefined)
    .map(node => (node.fullName, node.filename))
    .l

  // Process by each function name and filename
  function_names.foreach { case (function_name, filename) =>
    val func_details = cpg.method
      .filter(y => y.fullName == function_name && y.filename == filename)
      .filter(node => node.lineNumber.isDefined && node.lineNumberEnd.isDefined && node.body.typeFullName != "<empty>")
      .map { x =>
        val cfg = if (!no_cfg) x.dotCfg.l else List.empty
        val ddg = if (!no_ddg) x.dotDdg.l else List.empty
        val ast = if (!no_ast) x.dotAst.l else List.empty

        (
          x.fullName,
          x.filename,
          x.lineNumber.getOrElse(0),
          x.lineNumberEnd.getOrElse(None),
          x.signature,
          x.name,
          x.signature,
          if (!no_metadata) x.controlStructure.filter(_.controlStructureType == "GOTO").code.l else List.empty,
          if (!no_metadata) x.call.name.l else List.empty,
          if (!no_metadata) x.controlStructure.condition.code.l else List.empty,
          cfg,
          ddg,
          ast
        )
      }
      .l
      .map { case (
        fullfuncname,
        filename,
        start_line,
        end_line,
        func_return_type,
        name,
        signature,
        gotos,
        calls,
        control_structures,
        cfg,
        ddg,
        ast
      ) =>
        function_name -> Map(
          "fullfuncname" -> fullfuncname,
          "filename" -> filename,
          "start_line" -> start_line,
          "end_line" -> end_line,
          "func_return_type" -> func_return_type,
          "name" -> name,
          "signature" -> signature,
          "gotos" -> gotos,
          "calls" -> calls,
          "control_structures" -> control_structures,
          "cfg" -> cfg,
          "ddg" -> ddg,
          "ast" -> ast
        )
      }.toMap

    val macro_count = if (!no_metadata) {
      cpg.method
        .filter(node => node.lineNumber.isDefined && node.lineNumberEnd.isDefined && node.body.typeFullName != "<empty>")
        .filter(_.fullName == function_name)
        .where(_.body.typeFullName("ANY"))
        .size
    } else 0

    if (func_details.nonEmpty && func_details.contains(function_name)) {
      val tmp_ret: Any = func_details(function_name)("func_return_type")
      val func_return_type = tmp_ret match {
        case s: String =>
          val returnType = s.split("\\(", 2)(0)
          returnType
        case _ =>
          println("Function return type is not a string or not found.")
          ""
      }

      val function_data_dump = Map(
        "name" -> func_details(function_name)("name"),
        "fullname" -> func_details(function_name)("fullfuncname"),
        "filename" -> func_details(function_name)("filename"),
        "return_type" -> (if (!no_metadata) func_return_type else ""),
        "macro_count" -> macro_count,
        "start_line" -> func_details(function_name)("start_line"),
        "end_line" -> func_details(function_name)("end_line"),
        "signature" -> func_details(function_name)("signature"),
        "gotos" -> func_details(function_name)("gotos"),
        "calls" -> func_details(function_name)("calls"),
        "control_structures" -> func_details(function_name)("control_structures"),
        "cfg" -> func_details(function_name)("cfg"),
        "ddg" -> func_details(function_name)("ddg"),
        "ast" -> func_details(function_name)("ast")
      )

      val json_function_data_dump = toJson_pp(function_data_dump)
      println("PYJOERN_DATA_START")
      println(json_function_data_dump)
      println("PYJOERN_DATA_END")
    }
  }
}
