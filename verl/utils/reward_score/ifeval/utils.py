from .instruction import (
    KeywordChecker,
    KeywordFrequencyChecker,
    ForbiddenWords,
    LetterFrequencyChecker,
    ResponseLanguageChecker,
    NumberOfSentences,
    ParagraphChecker,
    NumberOfWords,
    ParagraphFirstWordCheck,
    PlaceholderChecker,
    PostscriptChecker,
    BulletListChecker,
    ConstrainedResponseChecker,
    HighlightSectionChecker,
    SectionChecker,
    JsonFormat,
    TitleChecker,
    TwoResponsesChecker,
    RepeatPromptThenAnswer,
    EndChecker,
    CapitalWordFrequencyChecker,
    CapitalLettersEnglishChecker,
    LowercaseLettersEnglishChecker,
    CommaChecker,
    QuotationChecker,
)

_KEYWORD = "keywords:"

_LANGUAGE = "language:"

_LENGTH = "length_constraints:"

_CONTENT = "detectable_content:"

_FORMAT = "detectable_format:"

_MULTITURN = "multi-turn:"

_COMBINATION = "combination:"

_STARTEND = "startend:"

_CHANGE_CASES = "change_case:"

_PUNCTUATION = "punctuation:"

INSTRUCTION_DICT = {
    _KEYWORD + "existence": KeywordChecker,
    _KEYWORD + "frequency": KeywordFrequencyChecker,
    _KEYWORD + "forbidden_words": ForbiddenWords,
    _KEYWORD + "letter_frequency": LetterFrequencyChecker,
    _LANGUAGE + "response_language": ResponseLanguageChecker,
    _LENGTH + "number_sentences": NumberOfSentences,
    _LENGTH + "number_paragraphs": ParagraphChecker,
    _LENGTH + "number_words": NumberOfWords,
    _LENGTH + "nth_paragraph_first_word": ParagraphFirstWordCheck,
    _CONTENT + "number_placeholders": PlaceholderChecker,
    _CONTENT + "postscript": PostscriptChecker,
    _FORMAT + "number_bullet_lists": BulletListChecker,
    # TODO(jeffreyzhou): Pre-create paragraph or use prompt to replace
    # _CONTENT + "rephrase_paragraph": RephraseParagraph,
    _FORMAT + "constrained_response": ConstrainedResponseChecker,
    _FORMAT + "number_highlighted_sections": (HighlightSectionChecker),
    _FORMAT + "multiple_sections": SectionChecker,
    # TODO(tianjianlu): Re-enable rephrasing with preprocessing the message.
    # _FORMAT + "rephrase": RephraseChecker,
    _FORMAT + "json_format": JsonFormat,
    _FORMAT + "title": TitleChecker,
    # TODO(tianjianlu): Re-enable with specific prompts.
    # _MULTITURN + "constrained_start": ConstrainedStartChecker,
    _COMBINATION + "two_responses": TwoResponsesChecker,
    _COMBINATION + "repeat_prompt": RepeatPromptThenAnswer,
    _STARTEND + "end_checker": EndChecker,
    _CHANGE_CASES + "capital_word_frequency": CapitalWordFrequencyChecker,
    _CHANGE_CASES + "english_capital": CapitalLettersEnglishChecker,
    _CHANGE_CASES + "english_lowercase": LowercaseLettersEnglishChecker,
    _PUNCTUATION + "no_comma": CommaChecker,
    _STARTEND + "quotation": QuotationChecker,
}

INSTRUCTION_CONFLICTS = {
    _KEYWORD + "existence": {_KEYWORD + "existence"},
    _KEYWORD + "frequency": {_KEYWORD + "frequency"},
    # TODO(jeffreyzhou): make a proper set of sentences to choose from
    # _KEYWORD + "key_sentences": KeySentenceChecker,
    _KEYWORD + "forbidden_words": {_KEYWORD + "forbidden_words"},
    _KEYWORD + "letter_frequency": {_KEYWORD + "letter_frequency"},
    _LANGUAGE + "response_language": {
        _LANGUAGE + "response_language",
        _FORMAT + "multiple_sections",
        _KEYWORD + "existence",
        _KEYWORD + "frequency",
        _KEYWORD + "forbidden_words",
        _STARTEND + "end_checker",
        _CHANGE_CASES + "english_capital",
        _CHANGE_CASES + "english_lowercase",
    },
    _LENGTH + "number_sentences": {_LENGTH + "number_sentences"},
    _LENGTH + "number_paragraphs": {
        _LENGTH + "number_paragraphs",
        _LENGTH + "nth_paragraph_first_word",
        _LENGTH + "number_sentences",
        _LENGTH + "nth_paragraph_first_word",
    },
    _LENGTH + "number_words": {_LENGTH + "number_words"},
    _LENGTH + "nth_paragraph_first_word": {
        _LENGTH + "nth_paragraph_first_word",
        _LENGTH + "number_paragraphs",
    },
    _CONTENT + "number_placeholders": {_CONTENT + "number_placeholders"},
    _CONTENT + "postscript": {_CONTENT + "postscript"},
    _FORMAT + "number_bullet_lists": {_FORMAT + "number_bullet_lists"},
    # TODO(jeffreyzhou): Pre-create paragraph or use prompt to replace
    # _CONTENT + "rephrase_paragraph": RephraseParagraph,
    _FORMAT + "constrained_response": set(INSTRUCTION_DICT.keys()),
    _FORMAT + "number_highlighted_sections": {_FORMAT + "number_highlighted_sections"},
    _FORMAT + "multiple_sections": {
        _FORMAT + "multiple_sections",
        _LANGUAGE + "response_language",
        _FORMAT + "number_highlighted_sections",
    },
    # TODO(tianjianlu): Re-enable rephrasing with preprocessing the message.
    # _FORMAT + "rephrase": RephraseChecker,
    _FORMAT + "json_format": set(INSTRUCTION_DICT.keys()).difference(
        {_KEYWORD + "forbidden_words", _KEYWORD + "existence"}
    ),
    _FORMAT + "title": {_FORMAT + "title"},
    # TODO(tianjianlu): Re-enable with specific prompts.
    # _MULTITURN + "constrained_start": ConstrainedStartChecker,
    _COMBINATION + "two_responses": set(INSTRUCTION_DICT.keys()).difference(
        {
            _KEYWORD + "forbidden_words",
            _KEYWORD + "existence",
            _LANGUAGE + "response_language",
            _FORMAT + "title",
            _PUNCTUATION + "no_comma",
        }
    ),
    _COMBINATION + "repeat_prompt": set(INSTRUCTION_DICT.keys()).difference(
        {_KEYWORD + "existence", _FORMAT + "title", _PUNCTUATION + "no_comma"}
    ),
    _STARTEND + "end_checker": {_STARTEND + "end_checker"},
    _CHANGE_CASES + "capital_word_frequency": {
        _CHANGE_CASES + "capital_word_frequency",
        _CHANGE_CASES + "english_lowercase",
        _CHANGE_CASES + "english_capital",
    },
    _CHANGE_CASES + "english_capital": {_CHANGE_CASES + "english_capital"},
    _CHANGE_CASES + "english_lowercase": {
        _CHANGE_CASES + "english_lowercase",
        _CHANGE_CASES + "english_capital",
    },
    _PUNCTUATION + "no_comma": {_PUNCTUATION + "no_comma"},
    _STARTEND + "quotation": {_STARTEND + "quotation", _FORMAT + "title"},
}


def conflict_make(conflicts):
    """Makes sure if A conflicts with B, B will conflict with A.

    Args:
      conflicts: Dictionary of potential conflicts where key is instruction id
        and value is set of instruction ids that it conflicts with.

    Returns:
      Revised version of the dictionary. All instructions conflict with
      themselves. If A conflicts with B, B will conflict with A.
    """
    for key in conflicts:
        for k in conflicts[key]:
            conflicts[k].add(key)
        conflicts[key].add(key)
    return conflicts

def compute_rule_score(
    response,
    inp,
):
    """Tests response to see if instructions are followed."""
    instruction_list = inp['instruction_id_list']
    is_following_list = []

    for index, instruction_id in enumerate(instruction_list):
        instruction_cls = INSTRUCTION_DICT[instruction_id]
        instruction = instruction_cls(instruction_id)

        # Remove None values from kwargs to avoid unexpected keyword argument errors in build_description method.
        kwargs = {k: v for k, v in inp['kwargs'][index].items() if v}
        instruction.build_description(**kwargs)
        args = instruction.get_instruction_args()
        if args and "prompt" in args:
            instruction.build_description(prompt=inp['prompt'])

        if response.strip() and instruction.check_following(response):
            is_following_list.append(True)
        else:
            is_following_list.append(False)

    return is_following_list