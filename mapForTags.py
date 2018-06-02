map_for_tags = {"NOUN": ["NN", "NNS", "NNS$", "NP", "NP$", "NPS", "NPS$", "NR"],  # существительное
                "VERB": ["VB", "VBG", "VBN", "VBP", "VBZ", "MD", "HV", "HVD", "HVG", "HVN", "DO", "DOD", "DOZ", "BE",
                         "BED", "BEDZ", "BEG", "BEM", "BEN", "BER", "BEZ"],  # глагол
                "ADV": ["RB", "RBR", "RBT", "RN", "WQL", "WRB", "RP", "RN", "QL", "QLP", "OD", "ABL"],  # наречие
                "ADJ": ["JJ", "JJR", "JJS", "JJT", "AP"],  # прилагательное
                "PRON": ["PN", "PN$", "PP$", "PP$$", "PPL", "PPLS", "PPO", "PPS", "PPSS", "PRP", "PRP$", "WPS", "WPO",
                         "WP$", "WDT"],  # местоимение
                "PREP": ["IN"],  # предлог
                "CONJ/DET": ["CC", "CS", "DT", "DTI", "DTS", "DTX", "AT", "ABX", "ABN"],
                # союзы, предлоги и определители
                "OTHER": ["UH", "EX", "FW", "TO", "CD"]
                }

map_for_parts_of_speech = {"NOUN": {"ru": "Существительное", "eng": "Noun"},  # существительное
                           "VERB": {"ru": "Глагол", "eng": "Verb"},  # глагол
                           "ADV": {"ru": "Наречие", "eng": "Adverb"},  # наречие
                           "ADJ": {"ru": "Прилагательное", "eng": "Adjective"},  # прилагательное
                           "PRON": {"ru": "Местоимение", "eng": "Pronoun"},  # местоимение
                           "PREP": {"ru": "Предлог", "eng": "Preposition"},  # предлог
                           "CONJ/DET": {"ru": "Союзы и определители", "eng": "Сonjunctions and determinants"},
                           # союзы и определители
                           "OTHER": {"ru": "Другое", "eng": "Other"}}
# print(nltk.pos_tag(["quite"], tagset='universal'))
