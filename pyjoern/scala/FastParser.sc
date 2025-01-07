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

@main def exec(target_dir: String) = {
  val cpg = importCode(target_dir)
  val function_names = cpg.method.filter(node => node.lineNumber != None && node.lineNumberEnd != None).map(node => (node.fullName, node.filename)).l

  // Process by each function name and filename
  function_names.foreach { case (function_name, filename) =>
    val func_details = cpg.method.filter(y => y.fullName == function_name && y.filename == filename)
      // filter all declarations (functions with no code)
      .filter(node => node.lineNumber!=None&&node.lineNumberEnd!=None&&node.body.typeFullName!="<empty>")
      .map(x => (
        x.fullName,
        x.filename,
        x.lineNumber.getOrElse(0),
        x.lineNumberEnd.getOrElse(None),
        x.signature,
        x.name,
        x.signature,
        x.controlStructure.filter(_.controlStructureType == "GOTO").code.l,
        x.call.name.l,
        x.controlStructure.condition.code.l,
        x.dotCfg.l,
        x.dotDdg.l,
        x.dotAst.l
      ))
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

    val macro_count = cpg.method
      .filter(node => node.lineNumber!=None&&node.lineNumberEnd!=None&&node.body.typeFullName!="<empty>")
      .filter(_.fullName==function_name)
      .where(_.body.typeFullName("ANY"))
      .size

    // Check if func_details for the current function_name is empty or not
    if (!func_details.isEmpty && func_details.contains(function_name)) {
      // function return type splitting!
      val tmp_ret: Any = func_details.get(function_name).get("func_return_type")
      val func_return_type = tmp_ret match {
        case s: String =>
          val returnType = s.split("\\(", 2)(0)  // Split by "(", limit to 2 parts, and take the first part
          returnType  // This value will be returned by the match expression
        case _ =>
          println("Function return type is not a string or not found.")
          ""  // Return an empty string or some default value if the return type is not found
      }

      val function_data_dump = Map(
        "name" -> func_details.get(function_name).get("name"),
        "fullname" -> func_details.get(function_name).get("fullfuncname"),
        "filename" -> func_details.get(function_name).get("filename"),
        "return_type" -> func_return_type,
        "macro_count" -> macro_count,
        "start_line" -> func_details.get(function_name).get("start_line"),
        "end_line" -> func_details.get(function_name).get("end_line"),
        "signature" -> func_details.get(function_name).get("signature"),
        "gotos" -> func_details.get(function_name).get("gotos"),
        "calls" -> func_details.get(function_name).get("calls"),
        "control_structures" -> func_details.get(function_name).get("control_structures"),
        "cfg" -> func_details.get(function_name).get("cfg"),
        "ddg" -> func_details.get(function_name).get("ddg"),
        "ast" -> func_details.get(function_name).get("ast")
      )

      // Convert function_data_dump to JSON string
      val json_function_data_dump = toJson_pp(function_data_dump)
      println("PYJOERN_DATA_START")
      println(json_function_data_dump)
      println("PYJOERN_DATA_END")
    }}
}