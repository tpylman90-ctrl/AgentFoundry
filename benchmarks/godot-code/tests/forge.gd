extends SceneTree

func check(label: String, ok: bool) -> void:
	print("AF_TEST:" + label + ":" + ("PASS" if ok else "FAIL"))

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var script = load("res://generated.gd")
	if script == null:
		quit(1)
		return
	var x = script.new()
	var recipes := {"blade":{"region":"forest","materials":{"iron":3,"wood":2},"output":"blade_item"},"dune":{"region":"desert","materials":{"iron":1},"output":"dune_item"},"invalid":{"region":"forest","materials":{"iron":0},"output":"free_item"}}
	x.configure({"iron":5,"wood":4,"blade_item":2}, recipes, ["forest"])
	check("F01", x.inventory().get("iron") == 5 and x.inventory().get("blade_item") == 2)
	check("F02", x.craft("blade") == true and x.inventory().get("iron") == 2 and x.inventory().get("wood") == 2)
	check("F03", x.inventory().get("blade_item") == 3)
	var before = x.inventory().duplicate(true)
	check("F04", x.craft("blade") == false and x.inventory() == before)
	check("F05", x.craft("dune") == false and x.inventory() == before)
	check("F06", x.craft("missing") == false and x.inventory() == before)
	check("F07", x.craft("invalid") == false and x.inventory() == before)
	x.configure({"iron":2,"wood":5}, recipes, ["forest","desert"])
	before = x.inventory().duplicate(true)
	check("F08", x.craft("blade") == false and x.inventory() == before)
	quit(0)
