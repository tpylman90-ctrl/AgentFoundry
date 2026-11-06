extends RefCounted
var quantities: Dictionary = {}
var recipes: Dictionary = {}
var regions: Array = []

func configure(stock: Dictionary, known: Dictionary, unlocked_regions: Array) -> void:
	quantities = stock.duplicate(true)
	recipes = known.duplicate(true)
	regions = unlocked_regions.duplicate(true)

func craft(recipe_id: String) -> bool:
	if not recipes.has(recipe_id):
		return false
	var recipe: Dictionary = recipes[recipe_id]
	if not str(recipe.get("region","")) in regions:
		return false
	var ingredients: Dictionary = recipe.get("materials",{})
	if ingredients.is_empty():
		return false
	for material in ingredients:
		var amount: int = int(ingredients[material])
		if amount <= 0 or int(quantities.get(material,0)) < amount:
			return false
	var result_id: String = str(recipe.get("output",""))
	if result_id.is_empty():
		return false
	for material in ingredients:
		quantities[material] = int(quantities.get(material,0)) - int(ingredients[material])
	quantities[result_id] = int(quantities.get(result_id,0)) + 1
	return true

func inventory() -> Dictionary:
	return quantities.duplicate(true)
