import pytest
from random import seed

from spin_the_wheel.words import SecretWord, InvalidLetter, HasGuessedLetterBefore, NothingLeftToGuess, RequiredField


@pytest.fixture(scope='module')
def path_to_words():
    return '../words/assets'


@pytest.fixture()
def secret_word():
    return SecretWord(word='Sabão em pó')


class Test___init__:
    def test_should_use_the_passed_word_as_the_secret_word(self):
        sw = SecretWord(word='Sabão em pó')

        assert sw.get_word() == 'SABÃO EM PÓ'
        assert sw.get_hidden_word().count('_') == 9
        assert sw.get_letter_count('a') == 2
        assert sw.get_letter_count('o') == 2
        assert sw.get_letter_count('e') == 1
        assert len(sw._previously_guessed_letters) == 0
        assert not sw.was_guessed

    def test_should_get_random_word_if_a_theme_is_passed(self):
        seed(3)
        sw = SecretWord('video_games')

        assert sw.get_word() == 'ASTRO BOT'
        assert sw.get_hidden_word().count('_') == 8
        assert sw.get_letter_count('a') == 1
        assert sw.get_letter_count('o') == 2
        assert sw.get_letter_count('e') == 0
        assert sw.get_letter_count('t') == 2
        assert len(sw._previously_guessed_letters) == 0
        assert not sw.was_guessed

    def test_should_raise_error_if_no_theme_or_word_is_passed(self):
        with pytest.raises(RequiredField):
            SecretWord()


class Test__get_random_secret_word:
    def test_should_raise_error_if_no_word_or_theme_is_passed(self):
        with pytest.raises(TypeError):
            SecretWord._get_random_secret_word()

    def test_should_get_random_word_from_theme(self):
        theme = 'fruits'
        seed(3)
        word = SecretWord._get_random_secret_word(theme)
        assert word == 'banana'

    def test_should_throw_error_if_the_theme_doesnt_exists(self):
        with pytest.raises(FileNotFoundError):
            SecretWord._get_random_secret_word('a9s7d9a87sd9')


class Test__is_letter_valid:
    def test_should_return_true_for_number(self):
        from_number = SecretWord._is_letter_valid('1')
        assert from_number

    def test_should_return_true_for_lower_cased_letter(self):
        from_lower_letter = SecretWord._is_letter_valid('a')
        assert from_lower_letter

    def test_should_return_true_for_upper_case_letter(self):
        from_upper_letter = SecretWord._is_letter_valid('A')
        assert from_upper_letter

    def test_should_return_true_for_letter_with_accentuation(self):
        from_letter_with_accentuation = SecretWord._is_letter_valid('Á')
        assert from_letter_with_accentuation

    def test_should_return_false_for_special_characters(self):
        from_underscore = SecretWord._is_letter_valid('_')
        from_dash = SecretWord._is_letter_valid('-')
        from_exclamation = SecretWord._is_letter_valid('!')
        from_space = SecretWord._is_letter_valid(' ')

        assert not from_underscore
        assert not from_dash
        assert not from_exclamation
        assert not from_space


class Test__normalize_letter:
    def test_should_return_upper_cased_letter(self):
        letter = SecretWord._normalize_letter('z')
        assert letter == 'Z'

    def test_should_strip_all_spaces_before_and_after_the_letter(self):
        letter = SecretWord._normalize_letter('     a     ')
        assert letter == 'A'

    def test_should_return_accented_letter_without_accentuation(self):
        letter = SecretWord._normalize_letter('á')
        assert letter == 'A'

    def test_should_return_only_the_first_letter_if_a_word_is_given(self):
        letter = SecretWord._normalize_letter('word')
        assert letter == 'W'


class Test__map_positions:
    def test_should_only_map_valid_letters(self):
        sw = SecretWord(word='Spider-Man 3: Venom')
        mapped_positions = sw._map_positions()

        assert len(mapped_positions['E']) == 2
        assert len(mapped_positions['S']) == 1
        assert len(mapped_positions['3']) == 1
        assert len(mapped_positions[' ']) == 0
        assert len(mapped_positions['-']) == 0
        assert len(mapped_positions[':']) == 0

    def test_should_map_letters_with_and_without_accentuation_as_the_same(self, secret_word):
        sw = secret_word
        mapped_positions = sw._map_positions()

        print('space', mapped_positions)

        assert len(mapped_positions['A']) == 2
        assert len(mapped_positions['O']) == 2
        assert len(mapped_positions['S']) == 1
        assert len(mapped_positions['B']) == 1


class Test__create_hidden_word:
    def test_should_return_the_word_as_a_list_with_valid_letters_replaced(self):
        sw = SecretWord(word='Spider-Man 3: Venom')
        hidden_word = sw._create_hidden_word()

        assert ' '.join(hidden_word) == '_ _ _ _ _ _ - _ _ _   _ :   _ _ _ _ _'

    def test_should_replace_letters_with_accentuation(self, secret_word):
        sw = secret_word
        hidden_word = sw._create_hidden_word()

        assert ' '.join(hidden_word) == '_ _ _ _ _   _ _   _ _'


class Test_get_word:
    def test_should_return_a_upper_cased_and_stripped_word(self):
        og_word = ' la casa de papel '
        sw = SecretWord(word=og_word)
        word = sw.get_word()

        assert word == og_word.upper().strip()

    def test_should_return_the_value_set_for__secret_word(self):
        og_word = 'just a test'
        sw = SecretWord(word='a')
        sw._secret_word = 'just a test'
        word = sw.get_word()

        assert word == og_word


class Test_get_hidden_word:
    def test_should_return_the_word_as_a_list_with_valid_letters_replaced(self):
        og_word = 'Spider-Man 3: Venom'
        sw = SecretWord(word=og_word)
        hidden_word = sw.get_hidden_word()

        assert ' '.join(hidden_word) == '_ _ _ _ _ _ - _ _ _   _ :   _ _ _ _ _'

    def test_should_return_the_value_set_for__hidden_word(self):
        og_word = 'just a test'
        sw = SecretWord(word='a')
        sw._hidden_word = 'just a test'
        word = sw.get_hidden_word()

        assert word == og_word


class Test_reveal_letter:
    def test_should_raise_error_if_try_to_guess_invalid_character(self, secret_word):
        with pytest.raises(InvalidLetter):
            secret_word.reveal_letter('@')

    def test_should_return_true_if_has_guessed_letter(self, secret_word):
        has_guessed_letter = secret_word.reveal_letter('a')
        assert has_guessed_letter

    def test_should_return_false_if_has_not_guessed_letter(self, secret_word):
        has_guessed_letter = secret_word.reveal_letter('z')
        assert not has_guessed_letter

    def test_should_not_change_hidden_word_on_invalid_or_not_found_letter(self, secret_word):
        hidden_word = ' '.join(secret_word.get_hidden_word())

        secret_word.reveal_letter('z')
        try:
            secret_word.reveal_letter('@')
        except InvalidLetter:
            pass

        new_hidden_word = ' '.join(secret_word.get_hidden_word())
        assert hidden_word == new_hidden_word
        assert hidden_word.count('_') == 9

    def test_should_replace_all_placeholders_that_match_the_letter(self, secret_word):
        hidden_word = ' '.join(secret_word.get_hidden_word())
        secret_word.reveal_letter('o')
        new_hidden_word = ' '.join(secret_word.get_hidden_word())

        assert hidden_word != new_hidden_word
        assert hidden_word.count('_') == 9
        assert new_hidden_word.count('_') == 7

    def test_should_display_accented_letters_as_accented_when_guessed(self, secret_word):
        hidden_word = ' '.join(secret_word.get_hidden_word())
        secret_word.reveal_letter('o')
        new_hidden_word = ' '.join(secret_word.get_hidden_word())

        assert hidden_word != new_hidden_word
        assert hidden_word.count('_') == 9
        assert new_hidden_word.count('_') == 7
        assert new_hidden_word.count('O') == 1
        assert new_hidden_word.count('Ó') == 1

    def test_should_not_change_was_guessed_until_guess_all_letters(self, secret_word):
        initial_was_guessed = secret_word.was_guessed
        secret_word.reveal_letter('s')
        one_letter_was_guessed = secret_word.was_guessed
        secret_word.reveal_letter('a')
        secret_word.reveal_letter('b')
        secret_word.reveal_letter('o')
        secret_word.reveal_letter('e')
        secret_word.reveal_letter('m')
        before_all_letters_was_guessed = secret_word.was_guessed

        assert not initial_was_guessed
        assert not one_letter_was_guessed
        assert not before_all_letters_was_guessed

    def test_should_only_change_was_guessed_after_guessing_all_letters(self, secret_word):
        initial_was_guessed = secret_word.was_guessed

        secret_word.reveal_letter('s')
        secret_word.reveal_letter('a')
        secret_word.reveal_letter('b')
        secret_word.reveal_letter('o')
        secret_word.reveal_letter('e')
        secret_word.reveal_letter('m')
        secret_word.reveal_letter('p')

        assert not initial_was_guessed
        assert secret_word.was_guessed

    def test_should_raise_error_when_guessing_the_same_letter(self, secret_word):
        with pytest.raises(HasGuessedLetterBefore):
            secret_word.reveal_letter('a')
            secret_word.reveal_letter('a')

    def test_should_raise_error_when_trying_to_guess_a_already_guessed_word(self, secret_word):
        with pytest.raises(NothingLeftToGuess):
            secret_word.reveal_letter('s')
            secret_word.reveal_letter('a')
            secret_word.reveal_letter('b')
            secret_word.reveal_letter('o')
            secret_word.reveal_letter('e')
            secret_word.reveal_letter('m')
            secret_word.reveal_letter('p')
            secret_word.reveal_letter('z')


class Test_has_letter:
    def test_should_return_true_if_has_letter(self):
        og_word = 'abc def hij'
        sw = SecretWord(word=og_word)

        assert sw.has_letter('A')
        assert sw.has_letter('B')
        assert sw.has_letter('D')

    def test_should_return_false_if_doesnt_have_letter(self):
        og_word = 'abc def hij'
        sw = SecretWord(word=og_word)

        assert not sw.has_letter('K')
        assert not sw.has_letter('R')
        assert not sw.has_letter('M')

    def test_should_not_care_about_case_sensitive(self):
        og_word = 'abc def hij'
        sw = SecretWord(word=og_word)

        assert sw.has_letter('a')
        assert sw.has_letter('b')
        assert sw.has_letter('c')


class Test_get_letter_count:
    def test_should_return_0_if_letter_is_not_found(self, secret_word):
        count = secret_word.get_letter_count('z')

        assert count == 0

    def test_should_return_the_number_of_times_the_letter_is_found(self, secret_word):
        count = secret_word.get_letter_count('a')

        assert count == 2
