def heal(game, caster):
    if caster == game.player:
        for bp_name in caster.creature.body_parts:
            caster.creature.body_parts[bp_name].heal(1)
    else:
        caster.creature.heal(1)
