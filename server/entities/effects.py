"""effect functions"""
import random
import math
from server.core.battle_manager import BattleEffectInfo

def damage_random_enemy(battle_effect_info:BattleEffectInfo):
    """damages a random enemy pet in the battle"""
    times_dict = {1:1, 2:2, 3:3}
    times = times_dict[battle_effect_info.effect_pet.level]
    pet_indices = battle_effect_info.enemy_loadout.pet_indices()
    for _ in range(times):
        if len(pet_indices) > 0:
            pet_index = random.randint(0, len(pet_indices) - 1)
            pet = battle_effect_info.enemy_loadout[pet_indices[pet_index]]
            pet.take_damage(1)
            pet_indices.pop(pet_index)

def copy_percent_health_from_the_healthiest_ally(battle_effect_info:BattleEffectInfo):
    """copy percentage of health from the healthiest ally"""
    percent_dict = {1:50, 2:100, 3:150}
    percent = percent_dict[battle_effect_info.effect_pet.level]
    healthiest_ally = battle_effect_info.pet_loadout.healthiest_pet()
    battle_effect_info.effect_pet.set_health(math.ceil(healthiest_ally.pet.health * (percent / 100)))

def give_percent_attack_to_friend_ahead(battle_effect_info:BattleEffectInfo):
    """gives percentage of its own attack to nearest friend ahead"""
    percent_dict = {1:50, 2:100, 3:150}
    percent = percent_dict[battle_effect_info.effect_pet.level]
    battle_effect_info.pet_loadout.friend_ahead(battle_effect_info.effect_pet).heal(math.floor(battle_effect_info.effect_pet.pet.attack * (percent / 100)))

def deal_4_damage_to_the_lowest_health_enemy(battle_effect_info:BattleEffectInfo):
    """deals 4 damage to the lowest health enemy/enemies"""
    times_dict = {1:1, 2:2, 3:3}
    times = times_dict[battle_effect_info.effect_pet.level]
    for _ in range(times):
        weakest_enemy = battle_effect_info.enemy_loadout.weakest_pet()
        if weakest_enemy is not None:
            weakest_enemy.take_damage(4)

def remove_percent_health_from_the_healthiest_enemy(battle_effect_info:BattleEffectInfo):
    """removes percentage of health from the healthiest enemy/enemy"""
    percent_dict = {1:33, 2:66, 3:99}
    percent = percent_dict[battle_effect_info.effect_pet.level]
    healthiest_enemy = battle_effect_info.enemy_loadout.healthiest_pet()
    healthiest_enemy.take_damage(math.floor(healthiest_enemy.pet.health * (percent / 100)))

def swallow_friend_ahead_and_release_it_on_faint(battle_effect_info:BattleEffectInfo):
    """swallows a friend ahead (release on faint is in a different function)"""
    friend_ahead = battle_effect_info.pet_loadout.friend_ahead(battle_effect_info.effect_pet)
    if friend_ahead is not None:
        battle_effect_info.effect_pet.swallow(friend_ahead)
        ahead_index = battle_effect_info.pet_loadout.pet_index(friend_ahead)
        if ahead_index is not None:
            battle_effect_info.pet_loadout[ahead_index] = None

def release_swallowed_friend(battle_effect_info:BattleEffectInfo, player_pet):
    """releases swallowed friend"""
    battle_effect_info.effect_pet.release_swallowed_friend()

effect_lookup ={
    "Deal damage to random enemy":damage_random_enemy,
    "Copy percent health from the healthiest ally":copy_percent_health_from_the_healthiest_ally,
    "Give percent attack to friend ahead":give_percent_attack_to_friend_ahead,
    "Deal 4 damage to the lowest health enemy":deal_4_damage_to_the_lowest_health_enemy,
    "Remove percent health from the healthiest enemy":remove_percent_health_from_the_healthiest_enemy,
    "Swallow friend ahead and release it on faint":swallow_friend_ahead_and_release_it_on_faint,
    "Release swallowed friend":release_swallowed_friend
}
