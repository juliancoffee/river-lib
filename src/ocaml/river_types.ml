type river_expr = Value of river_value
(* type river_expr = Value of river_value | Expr of river_expr *)
and river_value = Atom of river_atom | Collection of river_collection
(* and river_collection = List of river_expr list | Map of (string, river_expr) Hashtbl.t*)
and river_collection = List of river_expr list
and river_atom = Int of int | String of string
