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
	x.configure({"mp":30,"turns":5}, [{"hp":90,"max_hp":100,"poisoned":true},{"hp":0,"max_hp":100,"poisoned":true},{"hp":100,"max_hp":100,"poisoned":false}])
	check("A01", x.cast("heal",0) == true and x.snapshot()["allies"][0]["hp"] == 100)
	check("A02", x.snapshot()["caster"]["mp"] == 24 and x.snapshot()["caster"]["turns"] == 4)
	var before = x.snapshot().duplicate(true)
	check("A03", x.cast("heal",0) == false and x.snapshot() == before)
	check("A04", x.cast("heal",1) == false and x.snapshot() == before)
	check("A05", x.cast("cleanse",0) == true and x.snapshot()["allies"][0]["poisoned"] == false)
	check("A06", x.cast("revive",1) == true and x.snapshot()["allies"][1]["hp"] == 10 and x.snapshot()["allies"][1]["poisoned"] == false)
	before = x.snapshot().duplicate(true)
	check("A07", x.cast("heal",-1) == false and x.snapshot() == before)
	check("A08", x.cast("nonsense",0) == false and x.snapshot() == before)
	x.configure({"mp":5,"turns":2}, [{"hp":40,"max_hp":100,"poisoned":true}])
	before = x.snapshot().duplicate(true)
	check("A09", x.cast("heal",0) == false and x.snapshot() == before)
	quit(0)
