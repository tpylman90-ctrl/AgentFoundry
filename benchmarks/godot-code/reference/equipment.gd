extends RefCounted
var definitions: Dictionary = {}
var quantities: Dictionary = {}
var equipped: Dictionary = {"weapon":"none","offhand":"none"}

func configure(defs: Dictionary, inventory: Dictionary) -> void:
	definitions = defs.duplicate(true)
	quantities = inventory.duplicate(true)
	equipped = {"weapon":"none","offhand":"none"}

func equip(item_id: String) -> bool:
	if not definitions.has(item_id) or int(quantities.get(item_id,0)) <= 0:
		return false
	var item: Dictionary = definitions[item_id]
	var slot: String = str(item.get("slot",""))
	if not equipped.has(slot):
		return false
	if slot == "weapon" and bool(item.get("two_handed",false)) and equipped["offhand"] != "none":
		return false
	if slot == "offhand" and equipped["weapon"] != "none":
		var weapon: Dictionary = definitions.get(equipped["weapon"],{})
		if bool(weapon.get("two_handed",false)):
			return false
	equipped[slot] = item_id
	return true

func unequip(slot: String) -> bool:
	if not equipped.has(slot) or equipped[slot] == "none":
		return false
	equipped[slot] = "none"
	return true

func snapshot() -> Dictionary:
	return equipped.duplicate(true)
