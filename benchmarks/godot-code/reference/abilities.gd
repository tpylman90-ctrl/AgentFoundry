extends RefCounted
var caster: Dictionary = {}
var allies: Array = []

func configure(data: Dictionary, party: Array) -> void:
	caster = data.duplicate(true)
	allies = party.duplicate(true)

func cast(kind: String, target_index: int) -> bool:
	if target_index < 0 or target_index >= allies.size():
		return false
	var cost: int = 0
	if kind == "heal":
		cost = 6
	elif kind == "cleanse":
		cost = 4
	elif kind == "revive":
		cost = 12
	else:
		return false
	if int(caster.get("mp",0)) < cost or int(caster.get("turns",0)) <= 0:
		return false
	var target: Dictionary = allies[target_index]
	var hp: int = int(target.get("hp",0))
	var max_hp: int = int(target.get("max_hp",0))
	if kind == "heal":
		if hp <= 0 or hp >= max_hp:
			return false
		target["hp"] = mini(max_hp,hp+20)
	elif kind == "cleanse":
		if hp <= 0 or not bool(target.get("poisoned",false)):
			return false
		target["poisoned"] = false
	elif kind == "revive":
		if hp != 0 or max_hp <= 0:
			return false
		target["hp"] = mini(max_hp,10)
		target["poisoned"] = false
	caster["mp"] = int(caster["mp"]) - cost
	caster["turns"] = int(caster["turns"]) - 1
	allies[target_index] = target
	return true

func snapshot() -> Dictionary:
	return {"caster":caster.duplicate(true),"allies":allies.duplicate(true)}
