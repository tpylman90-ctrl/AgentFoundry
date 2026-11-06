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
	var defs := {"sword":{"slot":"weapon","two_handed":false},"greatsword":{"slot":"weapon","two_handed":true},"buckler":{"slot":"offhand"},"ghost":{"slot":"weapon","two_handed":false}}
	var amounts := {"sword":1,"greatsword":1,"buckler":1,"ghost":0}
	x.configure(defs, amounts)
	check("E01", x.snapshot().get("weapon") == "none" and x.snapshot().get("offhand") == "none")
	check("E02", x.equip("sword") == true and x.snapshot().get("weapon") == "sword")
	check("E03", x.equip("buckler") == true and x.snapshot().get("offhand") == "buckler")
	var before = x.snapshot().duplicate(true)
	check("E04", x.equip("greatsword") == false and x.snapshot() == before)
	check("E05", x.unequip("offhand") == true and x.snapshot().get("offhand") == "none")
	check("E06", x.equip("greatsword") == true and x.snapshot().get("weapon") == "greatsword")
	before = x.snapshot().duplicate(true)
	check("E07", x.equip("buckler") == false and x.snapshot() == before)
	check("E08", x.equip("ghost") == false and x.snapshot() == before)
	check("E09", x.unequip("unknown") == false and x.snapshot() == before)
	quit(0)
