"""effect functions"""
import random
import math
import json
from pathlib import Path
from entities.battle_effect_info import BattleEffectInfo, GameEffectInfo


def damage_random_enemy(battle_effect_info:BattleEffectInfo):
    """damages a random enemy pet in the battle"""
    times_dict = {1:1, 2:2, 3:3}
    times = times_dict[battle_effect_info.effect_pet.level]
    pet_indices = battle_effect_info.enemy_loadout.pet_indices()
    
    for _ in range(times):
        if len(pet_indices) > 0:
            if len(pet_indices) == 0:
                return
            pet_index = random.randint(0, len(pet_indices) - 1)
            pet = battle_effect_info.enemy_loadout[pet_indices[pet_index]]
            pet.take_damage(1)
            log = {"type":"damage",
                "attacker loadout": battle_effect_info.pet_loadout.index,
                "attacker":battle_effect_info.pet_loadout.pet_index(battle_effect_info.effect_pet),
                "target loadout":battle_effect_info.enemy_loadout.index,
                "target":pet_indices[pet_index],
                "damage":1}
            battle_effect_info.battle_manager.log.append(log)
            pet_indices.pop(pet_index)

def copy_percent_health_from_the_healthiest_ally(battle_effect_info:BattleEffectInfo):
    """copy percentage of health from the healthiest ally"""
    percent_dict = {1:50, 2:100, 3:150}
    percent = percent_dict[battle_effect_info.effect_pet.level]
    healthiest_ally = battle_effect_info.pet_loadout.healthiest_pet()
    if healthiest_ally is None:
        return
    new_health = math.ceil(healthiest_ally.pet.health * (percent / 100))
    battle_effect_info.effect_pet.set_health(new_health)
    battle_effect_info.battle_manager.log.append({"type":"set stats", "loadout": battle_effect_info.pet_loadout.index, "pet": battle_effect_info.pet_loadout.pet_index(battle_effect_info.effect_pet), "health": new_health})

def give_percent_attack_to_friend_ahead(battle_effect_info:BattleEffectInfo):
    """gives percentage of its own attack to nearest friend ahead"""
    percent_dict = {1:50, 2:100, 3:150}
    percent = percent_dict[battle_effect_info.effect_pet.level]
    att_amount = math.floor(battle_effect_info.effect_pet.pet.attack * (percent / 100))
    friend_ahead = battle_effect_info.pet_loadout.friend_ahead(battle_effect_info.effect_pet)
    if friend_ahead is None:
        return
    friend_ahead.pet.attack += att_amount
    log = {"type":"buff",
        "buffer loadout": battle_effect_info.pet_loadout.index,
        "buffer": battle_effect_info.pet_loadout.pet_index(battle_effect_info.effect_pet),
        "target loadout": battle_effect_info.pet_loadout.index,
        "target":battle_effect_info.pet_loadout.pet_index(friend_ahead),
        "amount":att_amount}
    battle_effect_info.battle_manager.log.append(log)

def deal_4_damage_to_the_lowest_health_enemy(battle_effect_info:BattleEffectInfo):
    """deals 4 damage to the lowest health enemy/enemies"""
    times_dict = {1:1, 2:2, 3:3}
    times = times_dict[battle_effect_info.effect_pet.level]
    for _ in range(times):
        weakest_enemy = battle_effect_info.enemy_loadout.weakest_pet()
        if weakest_enemy is not None:
            weakest_enemy.take_damage(4)
            log = {"type":"damage",
                "attacker loadout": battle_effect_info.pet_loadout.index,
                "attacker":battle_effect_info.pet_loadout.pet_index(battle_effect_info.effect_pet),
                "target loadout":battle_effect_info.enemy_loadout.index,
                "target":battle_effect_info.enemy_loadout.pet_index(weakest_enemy),
                "damage":4}
            battle_effect_info.battle_manager.log.append(log)

def remove_percent_health_from_the_healthiest_enemy(battle_effect_info:BattleEffectInfo):
    """removes percentage of health from the healthiest enemy/enemy"""
    percent_dict = {1:33, 2:66, 3:99}
    percent = percent_dict[battle_effect_info.effect_pet.level]
    healthiest_enemy = battle_effect_info.enemy_loadout.healthiest_pet()
    if healthiest_enemy is None:
        return
    damage_amount = math.floor(healthiest_enemy.pet.health * (percent / 100))
    healthiest_enemy.take_damage(damage_amount)
    log = {"type":"damage",
                "attacker loadout": battle_effect_info.pet_loadout.index,
                "attacker":battle_effect_info.pet_loadout.pet_index(battle_effect_info.effect_pet),
                "target loadout":battle_effect_info.enemy_loadout.index,
                "target":battle_effect_info.enemy_loadout.pet_index(healthiest_enemy),
                "damage":damage_amount}
    battle_effect_info.battle_manager.log.append(log)

def swallow_friend_ahead_and_release_it_on_faint(battle_effect_info:BattleEffectInfo):
    """swallows a friend ahead (release on faint is in a different function)"""
    friend_ahead = battle_effect_info.pet_loadout.friend_ahead(battle_effect_info.effect_pet)
    if friend_ahead is not None:
        battle_effect_info.effect_pet.pet.swallow(friend_ahead)
        ahead_index = battle_effect_info.pet_loadout.pet_index(friend_ahead)
        battle_effect_info.pet_loadout[ahead_index] = None
        log = {"type":"swallow",
            "swallowed loadout": battle_effect_info.pet_loadout.index,
            "swallowed":ahead_index,
            "swallower loadout": battle_effect_info.pet_loadout.index,
            "swallower":battle_effect_info.pet_loadout.pet_index(battle_effect_info.effect_pet)}
        battle_effect_info.battle_manager.log.append(log)

def release_swallowed_friend(battle_effect_info:BattleEffectInfo, **kwargs):
    """releases swallowed friend"""
    if kwargs["player_pet"] is not battle_effect_info.effect_pet:
        return
    if battle_effect_info.effect_pet.pet.swallowed is None:
        print("Nothing Swallowed")
        return
    level_dict = {1:1, 2:2, 3:3}
    xp_dict = {1:0, 2:2, 3:5}
    level = level_dict[battle_effect_info.effect_pet.level]
    xp = xp_dict[battle_effect_info.effect_pet.level]
    position = battle_effect_info.pet_loadout.pet_index(battle_effect_info.effect_pet)
    name = battle_effect_info.effect_pet.pet.swallowed
    json_path = Path(__file__).parent.parent / "data" / "pets.json"
    with open(json_path, "r") as file:
        data = json.load(file)
    pet_data = data[name]
    attack = pet_data["attack"] + xp
    health = pet_data["health"] + xp
    tier = pet_data["tier"]
    ability_class = pet_data["ability_class"]
    ability = pet_data["ability"]
    secondary_abilities = pet_data["secondary_abilities"] if "secondary_abilities" in pet_data else []
    log1 = {
        "type":"spit out",
        "swallower loadout": battle_effect_info.pet_loadout.index,
        "swallower": position
    }
    battle_effect_info.battle_manager.log.append(log1)
    if battle_effect_info.pet_loadout.summon_exact(name, attack, health, tier, ability_class, ability, secondary_abilities, xp, level, position):
        log2 = {
        "type":"summon",
        "position": position,
        "pet": name,
        "xp":xp,
        "level":level,
        "attack":attack,
        "health":health
        }
    else:
        log2 = {
        "type":"throw out",
        "thrower loadout": battle_effect_info.pet_loadout.index,
        "throwed": position
    }
    battle_effect_info.battle_manager.log.append(log2)
    battle_effect_info.effect_pet.pet.release_swallowed_pet()
    print(f"loadout1:{battle_effect_info.battle_manager.battle_loadout1}")
    print(f"loadout2:{battle_effect_info.battle_manager.battle_loadout2}\n")
    
def give_shop_pets_x_health(game_effect_info:GameEffectInfo, **kwargs):
    """gives shop pets x health"""
    if kwargs["player_pet"] is not game_effect_info.effect_pet:
        return
    hp_dict = {1:1, 2:2, 3:3}
    for shop_pet in game_effect_info.client.player.shop.shop_pets:
        shop_pet.pet.health += hp_dict[game_effect_info.effect_pet.level]

def give_two_random_friends_x_attack(game_effect_info:GameEffectInfo, **kwargs):
    """gives two random friends x attack"""
    if kwargs["player_pet"] is not game_effect_info.effect_pet:
        return
    attack_dict = {1:1, 2:2, 3:3}
    indices = game_effect_info.pet_loadout.pet_indices()
    for i,index in enumerate(indices):
        if index == game_effect_info.pet_loadout.pet_index(game_effect_info.effect_pet):
            indices.pop(i)
            break
    for _ in range(2):
        if len(indices) == 0:
            return
        random_num = random.randint(0, len(indices) - 1)
        friend = game_effect_info.pet_loadout[indices[random_num]]
        friend.pet.attack += attack_dict[game_effect_info.effect_pet.level]
        indices.pop(random_num)

def give_x_random_friends_1_health(game_effect_info:GameEffectInfo, **kwargs):
    """gives x random friends 1 health"""
    if kwargs["player_pet"] is not game_effect_info.effect_pet or not game_effect_info.effect_pet.alive:
        return
    hp_dict = {1:1, 2:2, 3:3}
    indices = game_effect_info.pet_loadout.pet_indices()
    for i,index in enumerate(indices):
        if index == game_effect_info.pet_loadout.pet_index(game_effect_info.effect_pet):
            indices.pop(i)
            break
    for _ in range(hp_dict[game_effect_info.effect_pet.level]):
        if len(indices) == 0:
            return
        random_num = random.randint(0, len(indices) - 1)
        friend = game_effect_info.pet_loadout[indices[random_num]]
        friend.pet.health += 1
        indices.pop(random_num)

def give_x_coins(game_effect_info:GameEffectInfo, **kwargs):
    """gives x coins"""
    if kwargs["player_pet"] is not game_effect_info.effect_pet or not game_effect_info.effect_pet.alive:
        return
    coin_dict = {1:1, 2:2, 3:3}
    game_effect_info.client.player.coins += coin_dict[game_effect_info.effect_pet.level]

def give_x_health_to_friends_if_lost(game_effect_info:GameEffectInfo, **kwargs):
    """gives x health to friends if lost"""
    if kwargs["player_pet"] is not game_effect_info.effect_pet or game_effect_info.effect_pet.alive:
        return
    hp_dict = {1:1, 2:2, 3:3}
    if game_effect_info.client.player.game_manager.last_loser is not game_effect_info.client.player:
        return
    for player_pet in game_effect_info.pet_loadout:
        if player_pet is not None and player_pet is not game_effect_info.effect_pet:
            player_pet.pet.health += hp_dict[game_effect_info.effect_pet.level]

def give_x_gold(game_effect_info:GameEffectInfo, **kwargs):
    """gives x gold"""
    if not game_effect_info.effect_pet.alive:
        return
    gold_dict = {1:1, 2:2, 3:3}
    game_effect_info.client.player.coins += gold_dict[game_effect_info.effect_pet.level]

def deal_x_damge_to_everyone(effect_info:BattleEffectInfo, **kwargs):
    """deals x damage to everyone"""
    if kwargs["player_pet"] is not effect_info.effect_pet:
        return
    damage_dict = {1:2, 2:4, 3:6}
    if effect_info.game_manager.client1.go_to_battle_phase and effect_info.game_manager.client2.go_to_battle_phase:
        for loadout in effect_info.battle_manager.loadouts:
            for player_pet in loadout:
                if player_pet is not None:
                    player_pet.take_damage(damage_dict[effect_info.effect_pet.level])
                    log = {"type":"damage",
                        "attacker loadout": effect_info.pet_loadout.index,
                        "attacker":effect_info.pet_loadout.pet_index(effect_info.effect_pet),
                        "target loadout":loadout.index,
                        "target":loadout.pet_index(player_pet),
                        "damage":damage_dict[effect_info.effect_pet.level]}
                    effect_info.battle_manager.log.append(log)
    else:
        for loadout in effect_info.game_manager.loadouts:
            for player_pet in loadout:
                if player_pet is not None:
                    player_pet.take_damage(damage_dict[effect_info.effect_pet.level])

effect_lookup ={
    "Deal damage to random enemy":damage_random_enemy,
    "Copy percent health from the healthiest ally":copy_percent_health_from_the_healthiest_ally,
    "Give percent attack to friend ahead":give_percent_attack_to_friend_ahead,
    "Deal 4 damage to the lowest health enemy":deal_4_damage_to_the_lowest_health_enemy,
    "Remove percent health from the healthiest enemy":remove_percent_health_from_the_healthiest_enemy,
    "Swallow friend ahead and release it on faint":swallow_friend_ahead_and_release_it_on_faint,
    "Release swallowed friend":release_swallowed_friend,
    "Give shop pets x health":give_shop_pets_x_health,
    "Give two random friends x attack":give_two_random_friends_x_attack,
    "Give x random friends 1 health":give_x_random_friends_1_health,
    "Give x coins":give_x_coins,
    "Give x health to friends if lost":give_x_health_to_friends_if_lost,
    "Give x gold":give_x_gold,
    "deal x damge to everyone":deal_x_damge_to_everyone
}
