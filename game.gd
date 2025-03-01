extends Node2D

@onready var countText: RichTextLabel = $UI/VBoxContainer/HBoxContainer/Count
@onready var button: Button = $UI/VBoxContainer/Button

var count: int = 0

func _ready() -> void:
	button.pressed.connect(add)
	refresh_count()

func refresh_count() -> void:
	countText.text = str(count)

func add() -> void:
	count += 1
	refresh_count()
