import pytest
import random
from unittest.mock import Mock, patch, MagicMock
from src.dungeon_game import DungeonGame

# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

def test_game_initialization_default_size():
    """Test game initializes with default 6x6 board."""
    game = DungeonGame()
    assert game.size == 6
    assert len(game.board) == 6
    assert len(game.board[0]) == 6

def test_game_initialization_custom_size():
    """Test game initializes with custom board size."""
    game = DungeonGame(size=10)
    assert game.size == 10
    assert len(game.board) == 10
    assert len(game.board[0]) == 10

def test_player_starts_at_origin():
    """Test player starts at position [0, 0]."""
    game = DungeonGame()
    assert game.player_pos == [0, 0]

def test_exit_at_bottom_right():
    """Test exit is placed at bottom-right corner."""
    game = DungeonGame(size=6)
    assert game.exit_pos == [5, 5]
    
    game = DungeonGame(size=10)
    assert game.exit_pos == [9, 9]

def test_initial_stats():
    """Test player starts with correct stats."""
    game = DungeonGame()
    assert game.hp == 100
    assert game.gold == 0
    assert game.game_over == False
    assert game.won == False

def test_initial_log_message():
    """Test welcome message in log."""
    game = DungeonGame()
    assert len(game.log) > 0
    assert "Welcome" in game.log[0]
    assert "Dungeon" in game.log[0]

def test_start_and_exit_positions_empty():
    """Test that start and exit positions are always empty."""
    for _ in range(10):  # Test multiple generations
        game = DungeonGame(size=6)
        assert game.board[0][0] == 0  # Start position
        assert game.board[5][5] == 0  # Exit position

# ============================================================================
# MAP GENERATION TESTS
# ============================================================================

def test_map_contains_events():
    """Test that map contains various event types."""
    game = DungeonGame(size=6)
    
    has_bug = any(1 in row for row in game.board)
    has_coffee = any(2 in row for row in game.board)
    has_feature = any(3 in row for row in game.board)
    
    # With random generation, at least some events should exist
    assert has_bug or has_coffee or has_feature

def test_map_generation_deterministic_with_seed():
    """Test map generation is deterministic with same random seed."""
    random.seed(42)
    game1 = DungeonGame(size=6)
    board1 = [row[:] for row in game1.board]
    
    random.seed(42)
    game2 = DungeonGame(size=6)
    board2 = [row[:] for row in game2.board]
    
    assert board1 == board2

def test_map_different_without_seed():
    """Test that maps are different without fixed seed."""
    game1 = DungeonGame(size=6)
    game2 = DungeonGame(size=6)
    
    # Boards should be different (very unlikely to be same)
    assert game1.board != game2.board

def test_map_event_distribution():
    """Test that events are distributed reasonably."""
    game = DungeonGame(size=10)
    
    bug_count = sum(row.count(1) for row in game.board)
    coffee_count = sum(row.count(2) for row in game.board)
    feature_count = sum(row.count(3) for row in game.board)
    
    # Should have some events (not zero for all)
    total_events = bug_count + coffee_count + feature_count
    assert total_events > 0

def test_small_map_generation():
    """Test map generation works for very small boards."""
    game = DungeonGame(size=2)
    assert game.size == 2
    assert game.board[0][0] == 0  # Start
    assert game.board[1][1] == 0  # Exit

def test_large_map_generation():
    """Test map generation works for large boards."""
    game = DungeonGame(size=20)
    assert game.size == 20
    assert len(game.board) == 20
    assert game.exit_pos == [19, 19]

# ============================================================================
# MOVEMENT TESTS
# ============================================================================

def test_move_right():
    """Test moving right increases column."""
    game = DungeonGame()
    game.move("RIGHT")
    assert game.player_pos == [0, 1]

def test_move_down():
    """Test moving down increases row."""
    game = DungeonGame()
    game.move("DOWN")
    assert game.player_pos == [1, 0]

def test_move_up():
    """Test moving up decreases row."""
    game = DungeonGame()
    game.move("DOWN")
    game.move("DOWN")
    game.move("UP")
    assert game.player_pos == [1, 0]

def test_move_left():
    """Test moving left decreases column."""
    game = DungeonGame()
    game.move("RIGHT")
    game.move("RIGHT")
    game.move("LEFT")
    assert game.player_pos == [0, 1]

def test_move_sequence():
    """Test a sequence of moves."""
    game = DungeonGame()
    game.move("RIGHT")
    game.move("RIGHT")
    game.move("DOWN")
    game.move("DOWN")
    assert game.player_pos == [2, 2]

def test_cannot_move_up_from_top():
    """Test cannot move up from top edge."""
    game = DungeonGame()
    initial_pos = game.player_pos[:]
    game.move("UP")
    assert game.player_pos == initial_pos
    assert "Can't move" in game.log[-1]

def test_cannot_move_left_from_left_edge():
    """Test cannot move left from left edge."""
    game = DungeonGame()
    initial_pos = game.player_pos[:]
    game.move("LEFT")
    assert game.player_pos == initial_pos
    assert "Can't move" in game.log[-1]

def test_cannot_move_down_from_bottom():
    """Test cannot move down from bottom edge."""
    game = DungeonGame(size=3)
    game.player_pos = [2, 0]  # Bottom edge
    initial_pos = game.player_pos[:]
    game.move("DOWN")
    assert game.player_pos == initial_pos

def test_cannot_move_right_from_right_edge():
    """Test cannot move right from right edge."""
    game = DungeonGame(size=3)
    game.player_pos = [0, 2]  # Right edge
    initial_pos = game.player_pos[:]
    game.move("RIGHT")
    assert game.player_pos == initial_pos

def test_invalid_direction():
    """Test invalid direction is handled."""
    game = DungeonGame()
    initial_pos = game.player_pos[:]
    game.move("DIAGONAL")
    assert game.player_pos == initial_pos

def test_movement_after_game_over():
    """Test cannot move after game is over."""
    game = DungeonGame()
    game.game_over = True
    initial_pos = game.player_pos[:]
    game.move("RIGHT")
    assert game.player_pos == initial_pos

# ============================================================================
# EVENT ENCOUNTER TESTS
# ============================================================================

def test_encounter_bug_damages_player():
    """Test encountering a bug reduces HP."""
    game = DungeonGame()
    game.board[0][1] = 1  # Place bug
    initial_hp = game.hp
    game.move("RIGHT")
    assert game.hp < initial_hp
    assert "Bug" in game.log[-1]

def test_encounter_coffee_heals_player():
    """Test encountering coffee increases HP."""
    game = DungeonGame()
    game.hp = 50
    game.board[0][1] = 2  # Place coffee
    game.move("RIGHT")
    assert game.hp > 50
    assert "coffee" in game.log[-1]

def test_coffee_cannot_exceed_max_hp():
    """Test coffee healing caps at 100 HP."""
    game = DungeonGame()
    game.hp = 95
    game.board[0][1] = 2  # Place coffee
    
    with patch('random.randint', return_value=20):  # Heal 20
        game.move("RIGHT")
    
    assert game.hp == 100

def test_encounter_feature_gives_gold():
    """Test encountering feature increases gold."""
    game = DungeonGame()
    initial_gold = game.gold
    game.board[0][1] = 3  # Place feature
    game.move("RIGHT")
    assert game.gold > initial_gold
    assert "feature" in game.log[-1]

def test_events_cleared_after_encounter():
    """Test events are removed after being encountered."""
    game = DungeonGame()
    game.board[0][1] = 1  # Place bug
    game.move("RIGHT")
    assert game.board[0][1] == 0  # Should be cleared

def test_bug_damage_range():
    """Test bug damage is within expected range."""
    game = DungeonGame()
    game.board[0][1] = 1
    initial_hp = game.hp
    game.move("RIGHT")
    damage = initial_hp - game.hp
    assert 10 <= damage <= 25

def test_coffee_heal_range():
    """Test coffee healing is within expected range."""
    game = DungeonGame()
    game.hp = 50
    game.board[0][1] = 2
    initial_hp = game.hp
    game.move("RIGHT")
    healing = game.hp - initial_hp
    assert 10 <= healing <= 20

def test_feature_gold_range():
    """Test feature gold is within expected range."""
    game = DungeonGame()
    game.board[0][1] = 3
    initial_gold = game.gold
    game.move("RIGHT")
    gold_gained = game.gold - initial_gold
    assert 100 <= gold_gained <= 500

# ============================================================================
# GAME OVER TESTS
# ============================================================================

def test_game_over_when_hp_zero():
    """Test game over when HP reaches zero."""
    game = DungeonGame()
    game.hp = 10
    game.board[0][1] = 1  # Place bug
    
    with patch('random.randint', return_value=25):  # Deal 25 damage
        game.move("RIGHT")
    
    assert game.hp <= 0
    assert game.game_over == True
    assert "Failed" in game.log[-1] or "won" in game.log[-1].lower()

def test_game_over_when_hp_negative():
    """Test game over even when HP goes negative."""
    game = DungeonGame()
    game.hp = 1
    game.board[0][1] = 1  # Place bug
    
    with patch('random.randint', return_value=25):  # Overkill damage
        game.move("RIGHT")
    
    assert game.hp < 0
    assert game.game_over == True

def test_multiple_bugs_can_kill_player():
    """Test multiple bug encounters can kill player."""
    game = DungeonGame()
    game.board[0][1] = 1
    game.board[0][2] = 1
    game.board[0][3] = 1
    game.board[0][4] = 1
    
    with patch('random.randint', return_value=25):
        for _ in range(4):
            if not game.game_over:
                game.move("RIGHT")
    
    assert game.game_over == True

# ============================================================================
# VICTORY TESTS
# ============================================================================

def test_win_by_reaching_exit():
    """Test winning by reaching the exit."""
    game = DungeonGame(size=3)
    game.player_pos = [2, 1]  # One step from exit
    game.move("RIGHT")
    assert game.won == True
    assert game.game_over == True
    assert "Production" in game.log[-1] or "deployed" in game.log[-1].lower()

def test_win_overrides_hp_zero():
    """Test that reaching exit wins even if HP would go to zero."""
    game = DungeonGame(size=2)
    game.hp = 1
    game.board[1][1] = 1  # Bug at exit (though exit should be clear)
    # In reality exit is always 0, but test the encounter logic
    game.player_pos = [1, 0]
    game.move("RIGHT")
    # Exit should trigger before bug damage
    assert game.won == True

def test_cannot_move_after_winning():
    """Test cannot move after winning."""
    game = DungeonGame(size=2)
    game.player_pos = [1, 0]
    game.move("RIGHT")
    assert game.won == True
    
    initial_pos = game.player_pos[:]
    game.move("DOWN")
    assert game.player_pos == initial_pos

# ============================================================================
# LOG TESTS
# ============================================================================

def test_log_records_movements():
    """Test log records game events."""
    game = DungeonGame()
    initial_log_length = len(game.log)
    game.board[0][1] = 1  # Place bug
    game.move("RIGHT")
    assert len(game.log) > initial_log_length

def test_log_records_invalid_moves():
    """Test log records invalid move attempts."""
    game = DungeonGame()
    game.move("UP")  # Invalid from start
    assert "Can't move" in game.log[-1]

def test_log_records_win():
    """Test log records victory."""
    game = DungeonGame(size=2)
    game.player_pos = [1, 0]
    game.move("RIGHT")
    assert any("Production" in msg or "deployed" in msg for msg in game.log)

def test_log_records_death():
    """Test log records death."""
    game = DungeonGame()
    game.hp = 1
    game.board[0][1] = 1
    
    with patch('random.randint', return_value=25):
        game.move("RIGHT")
    
    assert any("Failed" in msg or "bugs won" in msg for msg in game.log)

def test_log_persists_through_game():
    """Test log accumulates throughout game."""
    game = DungeonGame()
    game.board[0][1] = 2  # Coffee
    game.board[1][1] = 3  # Feature
    
    initial_length = len(game.log)
    game.move("RIGHT")
    game.move("DOWN")
    
    assert len(game.log) > initial_length

# ============================================================================
# EDGE CASES
# ============================================================================

def test_minimum_board_size():
    """Test game works with minimum 2x2 board."""
    game = DungeonGame(size=2)
    assert game.size == 2
    assert game.player_pos == [0, 0]
    assert game.exit_pos == [1, 1]

def test_single_cell_board():
    """Test behavior with 1x1 board (if allowed)."""
    try:
        game = DungeonGame(size=1)
        # Player and exit would be same position
        assert game.player_pos == game.exit_pos
    except (ValueError, IndexError):
        # Expected - 1x1 board might not be supported
        pass

def test_survive_with_exactly_one_hp():
    """Test player survives when HP is exactly 1."""
    game = DungeonGame()
    game.hp = 1
    game.board[0][1] = 2  # Coffee to heal
    game.move("RIGHT")
    assert game.hp > 1
    assert game.game_over == False

def test_multiple_events_on_path():
    """Test encountering multiple events in sequence."""
    game = DungeonGame()
    game.board[0][1] = 2  # Coffee
    game.board[0][2] = 3  # Feature
    game.board[0][3] = 1  # Bug
    
    game.move("RIGHT")
    assert game.hp >= 100
    game.move("RIGHT")
    assert game.gold > 0
    game.move("RIGHT")
    assert game.hp < 100

def test_empty_path_to_exit():
    """Test reaching exit with no encounters."""
    game = DungeonGame(size=2)
    # Clear any events
    game.board[0][1] = 0
    game.board[1][0] = 0
    game.board[1][1] = 0
    
    initial_hp = game.hp
    initial_gold = game.gold
    
    game.move("RIGHT")
    game.move("DOWN")
    
    assert game.won == True
    assert game.hp == initial_hp
    assert game.gold == initial_gold

# ============================================================================
# STATS TRACKING TESTS
# ============================================================================

def test_gold_accumulates():
    """Test gold accumulates across multiple features."""
    game = DungeonGame()
    game.board[0][1] = 3
    game.board[0][2] = 3
    
    game.move("RIGHT")
    first_gold = game.gold
    game.move("RIGHT")
    
    assert game.gold > first_gold

def test_hp_changes_tracked():
    """Test HP changes are properly tracked."""
    game = DungeonGame()
    game.board[0][1] = 1  # Bug
    game.board[0][2] = 2  # Coffee
    
    game.move("RIGHT")
    hp_after_bug = game.hp
    assert hp_after_bug < 100
    
    game.move("RIGHT")
    assert game.hp > hp_after_bug

def test_negative_gold_not_possible():
    """Test gold never goes negative."""
    game = DungeonGame()
    assert game.gold == 0
    # No mechanics reduce gold, but verify it stays non-negative
    game.move("RIGHT")
    assert game.gold >= 0

# ============================================================================
# RANDOMNESS TESTS
# ============================================================================

def test_deterministic_with_mocked_random():
    """Test game is deterministic when random is mocked."""
    with patch('random.randint', return_value=15):
        game = DungeonGame()
        game.board[0][1] = 1  # Bug
        game.move("RIGHT")
        assert game.hp == 85  # 100 - 15

def test_random_ranges_respected():
    """Test that random values stay within defined ranges."""
    game = DungeonGame()
    
    # Test multiple events
    for i in range(10):
        game2 = DungeonGame()
        game2.board[0][1] = 1  # Bug
        game2.move("RIGHT")
        damage = 100 - game2.hp
        assert 10 <= damage <= 25

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_complete_game_win_scenario():
    """Test a complete game from start to win."""
    game = DungeonGame(size=3)
    # Create clear path to exit
    for i in range(3):
        for j in range(3):
            game.board[i][j] = 0
    
    # Move to exit
    game.move("RIGHT")
    game.move("RIGHT")
    game.move("DOWN")
    game.move("DOWN")
    
    assert game.won == True
    assert game.game_over == True
    assert game.player_pos == [2, 2]

def test_complete_game_lose_scenario():
    """Test a complete game from start to death."""
    game = DungeonGame()
    # Fill path with bugs
    game.board[0][1] = 1
    game.board[0][2] = 1
    game.board[0][3] = 1
    game.board[0][4] = 1
    
    with patch('random.randint', return_value=25):
        for _ in range(5):
            if not game.game_over:
                game.move("RIGHT")
    
    assert game.game_over == True
    assert game.won == False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])