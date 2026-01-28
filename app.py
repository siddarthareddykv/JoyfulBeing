import sys
import os
import datetime
import datetime
import calendar as pycalendar
from flask import Flask, render_template, request

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

from flask import Flask, render_template, request, jsonify
import calendar as pycalendar
import random

app = Flask(__name__)

# ============================================================================
# MONTH THEMES (elegant colors with seasonal harmony)
# ============================================================================
month_themes = {
    1:  {"bg": "#E3F2FD", "accent": "#1565C0", "name": "New Beginning", "emoji": "❄️"},
    2:  {"bg": "#FCE4EC", "accent": "#AD1457", "name": "Love & Compassion", "emoji": "💕"},
    3:  {"bg": "#E8F5E9", "accent": "#2E7D32", "name": "Growth & Renewal", "emoji": "🌱"},
    4:  {"bg": "#FFF8E1", "accent": "#FF8F00", "name": "Awakening", "emoji": "🌸"},
    5:  {"bg": "#F3E5F5", "accent": "#6A1B9A", "name": "Joy & Creativity", "emoji": "🦋"},
    6:  {"bg": "#E0F2F1", "accent": "#00695C", "name": "Harmony", "emoji": "🌊"},
    7:  {"bg": "#FFF3E0", "accent": "#EF6C00", "name": "Radiance", "emoji": "☀️"},
    8:  {"bg": "#F1F8E9", "accent": "#558B2F", "name": "Abundance", "emoji": "🌻"},
    9:  {"bg": "#EDE7F6", "accent": "#4527A0", "name": "Wisdom & Balance", "emoji": "🍂"},
    10: {"bg": "#FFFDE7", "accent": "#F9A825", "name": "Gratitude", "emoji": "🎃"},
    11: {"bg": "#ECEFF1", "accent": "#37474F", "name": "Reflection", "emoji": "🍁"},
    12: {"bg": "#E0F7FA", "accent": "#00838F", "name": "Peace & Hope", "emoji": "❄️✨"}
}

# ============================================================================
# MYTHOLOGY STORIES (Tales from Ramayana & Mahabharata)
# ============================================================================
mythology_stories = [
    {
        "title": "Rama's Dharma - The Path of Duty",
        "source": "Ramayana",
        "story": "Prince Rama, though entitled to the throne, chose exile for 14 years to honor his father's promise. This teaches us that true strength lies in fulfilling our duties with grace, not in claiming what is rightfully ours. Rama's unwavering commitment to dharma, even when it brought personal suffering, shows that integrity is life's greatest treasure.",
        "lesson": "Your duty is your dharma. Fulfill it with love, not expectation."
    },
    {
        "title": "Sita's Strength - Inner Light",
        "source": "Ramayana",
        "story": "Sita remained calm and centered during her captivity, never losing faith in Rama or herself. Though tested physically and emotionally, she emerged with her inner light intact. Her story teaches that no external circumstance can diminish the strength of a pure and centered mind.",
        "lesson": "Your inner light cannot be dimmed by external darkness."
    },
    {
        "title": "Hanuman's Devotion - Surrender to Purpose",
        "source": "Ramayana",
        "story": "Hanuman's complete devotion to Rama transformed him into an instrument of divine will. He didn't question; he served with all his heart. His story shows that when we surrender our ego and align with a higher purpose, we become capable of the impossible.",
        "lesson": "When you surrender your ego, divine strength flows through you."
    },
    {
        "title": "Arjuna's Crisis - The Power of Clarity",
        "source": "Mahabharata (Bhagavad Gita)",
        "story": "On the battlefield, Arjuna was paralyzed by doubt and confusion. Through Krishna's wisdom in the Bhagavad Gita, he gained clarity on his dharma and overcame his inner turmoil. This teaches us that confusion ends when we understand our true purpose.",
        "lesson": "Seek clarity when confused. Your purpose will set you free."
    },
    {
        "title": "Draupadi's Resilience - Dignity Over Defeat",
        "source": "Mahabharata",
        "story": "Though publicly humiliated, Draupadi never lost her dignity or her commitment to justice. She waited 13 years for her restoration, never losing faith. Her story shows that dignity is not given by others—it comes from within.",
        "lesson": "Your dignity is unbreakable. No one can take it unless you allow them to."
    },
    {
        "title": "Karna's Choice - The Weight of Decisions",
        "source": "Mahabharata",
        "story": "Karna, despite knowing the consequences, chose loyalty over wisdom. His story teaches that every choice has weight. We must choose consciously, with full understanding of the consequences, not just because of loyalty or emotion.",
        "lesson": "Choose with wisdom, not just with your heart. Both matter."
    },
    {
        "title": "Bhima's Patience - Strength Through Restraint",
        "source": "Mahabharata",
        "story": "Though Bhima had the strength to defeat his enemies immediately, he waited. He understood that the right time is as important as the right action. This teaches patience as a form of strength.",
        "lesson": "True strength knows when to act and when to wait."
    },
    {
        "title": "Kunti's Wisdom - The Mother's Teaching",
        "source": "Mahabharata",
        "story": "Kunti raised her sons with wisdom, teaching them dharma over comfort. She made the hardest choice—freeing Krishna—for the greater good. A mother's love combined with wisdom creates greatness.",
        "lesson": "Love with wisdom. Sometimes the hardest choice is the right one."
    }
]

# ============================================================================
# SANSKRIT MANTRAS (With Pronunciation & Meanings)
# ============================================================================
sanskrit_mantras = [
    {
        "mantra": "Om (ॐ)",
        "pronunciation": "Aum",
        "meaning": "The universal sound, representing the ultimate reality and consciousness",
        "benefits": "Grounding, spiritual connection, meditation foundation",
        "how_to_use": "Chant slowly with deep breath. Feel the vibration in your chest and head."
    },
    {
        "mantra": "So Hum (सो हम्)",
        "pronunciation": "So-Hum",
        "meaning": "I am That - the unity between self and universe",
        "benefits": "Self-realization, connection to cosmos, meditation focus",
        "how_to_use": "Inhale 'So', exhale 'Hum'. Synchronize with your natural breath."
    },
    {
        "mantra": "Aham Brahmasmi (अहं ब्रह्मास्मि)",
        "pronunciation": "Ah-hum Brah-mahs-mee",
        "meaning": "I am Brahman - the divine consciousness",
        "benefits": "Self-empowerment, ego dissolution, spiritual awakening",
        "how_to_use": "Repeat slowly 108 times. Feel yourself merging with infinite consciousness."
    },
    {
        "mantra": "Tat Tvam Asi (तत् त्वं असि)",
        "pronunciation": "Tat Tvum Ah-see",
        "meaning": "Thou art That - you are not separate from the divine",
        "benefits": "Non-duality understanding, peace, interconnectedness",
        "how_to_use": "Meditate on this truth. Realize your oneness with all existence."
    },
    {
        "mantra": "Gayatri Mantra (गायत्री मंत्र)",
        "pronunciation": "Om Bhur Bhuvah Svah, Tat Savitur Varenyam...",
        "meaning": "Invocation to the divine light within the sun, for enlightenment",
        "benefits": "Purification, spiritual growth, clarity of mind",
        "how_to_use": "Chant 108 times during sunrise. Feel the connection to divine light."
    },
    {
        "mantra": "Mahamantra (महामंत्र)",
        "pronunciation": "Hare Krishna, Hare Krishna, Krishna Krishna, Hare Hare, Hare Rama, Hare Rama, Rama Rama, Hare Hare",
        "meaning": "Calling upon divine names for liberation and joy",
        "benefits": "Devotion, joy, liberation from suffering",
        "how_to_use": "Chant with devotion, feeling the sweetness in each name."
    },
    {
        "mantra": "Maha Mrityunjaya Mantra (महामृत्यूंजय मंत्र)",
        "pronunciation": "Om Tryambakam Yajamahe...",
        "meaning": "The great mantra of death-defying power, for healing and longevity",
        "benefits": "Healing, protection, longevity, overcoming obstacles",
        "how_to_use": "Chant 108 times for health and well-being."
    },
    {
        "mantra": "Asatoma Sadgamaya (असतोमा सद्गमय)",
        "pronunciation": "Ah-sah-to-mah Sad-gah-mah-yah",
        "meaning": "Lead me from illusion to truth, from darkness to light",
        "benefits": "Spiritual progress, truth-seeking, inner transformation",
        "how_to_use": "Meditate on moving from ignorance to wisdom with each chant."
    }
]

# ============================================================================
# VEDIC RITUALS (Daily Practices for Wellness)
# ============================================================================
vedic_rituals = [
    {
        "name": "Surya Namaskara (Sun Salutation)",
        "time": "Early morning (sunrise preferred)",
        "duration": "10-15 minutes",
        "benefits": "Energizes body, connects with life force, improves flexibility",
        "steps": [
            "Stand facing the sunrise with hands in prayer",
            "Perform 12 salutations, synchronizing with breath",
            "Each round connects you with the sun's healing energy",
            "Feel gratitude for the light and warmth"
        ],
        "practice_tip": "Do 12 rounds for optimal benefit. Build gradually if new to practice."
    },
    {
        "name": "Sandhya Vandana (Prayer at Twilight)",
        "time": "Sunrise and sunset",
        "duration": "20-30 minutes",
        "benefits": "Connects you with cosmic rhythms, purifies mind, builds discipline",
        "steps": [
            "Face east at sunrise, west at sunset",
            "Perform water rituals symbolizing purification",
            "Recite mantras with focused intention",
            "Meditate on the transition between day and night"
        ],
        "practice_tip": "This ancient ritual aligns you with nature's rhythms."
    },
    {
        "name": "Pranayama (Breath Regulation)",
        "time": "Early morning or evening",
        "duration": "15-20 minutes",
        "benefits": "Purifies nadis (energy channels), calms mind, increases prana (life force)",
        "steps": [
            "Sit comfortably with spine straight",
            "Practice Nadi Shodhana (alternate nostril breathing)",
            "Follow with Ujjayi or Sama Vritti breathing",
            "End with natural breathing meditation"
        ],
        "practice_tip": "Empty your lungs fully. Quality over quantity matters."
    },
    {
        "name": "Abhyanga (Self-Oil Massage)",
        "time": "Early morning before bath",
        "duration": "15-20 minutes",
        "benefits": "Nourishes skin, calms nervous system, improves circulation",
        "steps": [
            "Warm sesame or coconut oil slightly",
            "Apply warm oil to entire body in circular motions",
            "Massage each body part with love and intention",
            "Let oil sit for 5-10 minutes before bathing"
        ],
        "practice_tip": "This is a form of self-love and healing. Feel the nurturing energy."
    },
    {
        "name": "Sattvic Eating (Mindful Eating)",
        "time": "All meals",
        "duration": "Varies",
        "benefits": "Purifies mind, increases clarity, improves digestion, raises consciousness",
        "steps": [
            "Eat foods in their natural form (fresh fruits, vegetables, grains)",
            "Eat mindfully, tasting each bite",
            "Avoid overeating—eat until 75% full",
            "Eat with gratitude and positive thoughts"
        ],
        "practice_tip": "Sattvic foods include: fruits, vegetables, whole grains, milk, honey, ghee, nuts."
    },
    {
        "name": "Meditation (Dhyana)",
        "time": "Early morning or evening",
        "duration": "20-45 minutes",
        "benefits": "Connects with inner self, reduces stress, brings clarity and peace",
        "steps": [
            "Sit in quiet space with spine straight",
            "Close eyes and focus on your breath or a mantra",
            "Let thoughts pass without judgment",
            "Rest in the silence and stillness"
        ],
        "practice_tip": "Consistency matters more than duration. Even 10 minutes daily transforms."
    },
    {
        "name": "Gratitude Ritual (Kriti Vidya)",
        "time": "Morning or before bed",
        "duration": "5-10 minutes",
        "benefits": "Shifts consciousness, attracts abundance, increases happiness",
        "steps": [
            "Sit quietly with closed eyes",
            "Recall 5 things you're grateful for today",
            "Feel the gratitude deeply in your heart",
            "Say a prayer of thanks to the universe"
        ],
        "practice_tip": "Gratitude is the fastest way to raise your vibration."
    },
    {
        "name": "Mudra Practice (Hand Gestures)",
        "time": "Anytime",
        "duration": "5-15 minutes",
        "benefits": "Balances energy, enhances meditation, heals emotional patterns",
        "steps": [
            "Learn specific hand positions (Gyan Mudra for knowledge, etc.)",
            "Hold mudra while meditating or breathing",
            "Feel the energy shift in your body",
            "Different mudras for different intentions"
        ],
        "practice_tip": "Gyan Mudra (thumb + index finger) is easiest for beginners."
    }
]

# ============================================================================
# SEASONAL PRACTICES (Practices Aligned with Seasons)
# ============================================================================
seasonal_practices = {
    "spring": {
        "season": "Spring (March-May)",
        "theme": "Renewal, Growth, Awakening",
        "practices": [
            "Early morning walks in nature to absorb spring energy",
            "Practice lighter yoga asanas focusing on flexibility",
            "Eat fresh, leafy greens and light foods",
            "Meditate on new beginnings and growth",
            "Perform cleansing rituals to release winter stagnation",
            "Chant mantras invoking growth and vitality"
        ],
        "affirmations": [
            "I am growing in wisdom and strength",
            "Fresh beginnings flow through me",
            "My potential blooms like spring flowers"
        ]
    },
    "summer": {
        "season": "Summer (June-August)",
        "theme": "Energy, Radiance, Action",
        "practices": [
            "Sunrise practices to connect with sun's power",
            "Cooling pranayama (Shitali breathing) to balance heat",
            "Eat cooling foods: coconut, watermelon, cucumber",
            "Meditate on inner light and radiance",
            "Engage in service and action (summer projects)",
            "Practice gratitude for abundance"
        ],
        "affirmations": [
            "My inner light shines brightly",
            "I radiate love and positivity",
            "My energy is unlimited and vibrant"
        ]
    },
    "autumn": {
        "season": "Autumn (September-November)",
        "theme": "Release, Reflection, Balance",
        "practices": [
            "Evening walks to reflect on the year",
            "Grounding practices to balance change",
            "Eat warming, grounding foods",
            "Journal about what to release and what to keep",
            "Practice detachment and non-attachment",
            "Gratitude rituals as harvest approaches"
        ],
        "affirmations": [
            "I release what no longer serves me",
            "I am grounded and balanced",
            "I harvest gratitude from my experiences"
        ]
    },
    "winter": {
        "season": "Winter (December-February)",
        "theme": "Introspection, Rest, Peace",
        "practices": [
            "Longer meditation and inward-looking practices",
            "Warming yoga and gentle movement",
            "Eat warming, nourishing foods (soups, grains)",
            "Create a cozy sacred space at home",
            "Reflect on the year and set intentions",
            "Practice self-care and rest",
            "Celebrate inner light (Diwali concept) even in darkness"
        ],
        "affirmations": [
            "I find peace in stillness",
            "My inner light glows even in darkness",
            "I am renewed and refreshed"
        ]
    }
}

# ============================================================================
# MOON PHASE PRACTICES (New Moon & Full Moon Activities)
# ============================================================================
moon_practices = {
    "new_moon": {
        "phase": "New Moon",
        "timing": "Occurs once per lunar month",
        "energy": "Introspection, new beginnings, planting seeds",
        "practices": [
            "Set intentions for the coming lunar cycle",
            "Meditate on what you want to manifest",
            "Write your goals and dreams in a journal",
            "Start new habits or projects",
            "Practice Chakra Meditation to align energy",
            "Chant manifestation mantras 108 times"
        ],
        "affirmations": [
            "I plant seeds of abundance",
            "New possibilities unfold before me",
            "I am a creator of my reality"
        ],
        "ritual": "Sit in darkness (blow out candles if safe), visualize your dreams, write them down, then read aloud with conviction."
    },
    "full_moon": {
        "phase": "Full Moon",
        "timing": "Occurs once per lunar month",
        "energy": "Release, completion, illumination, gratitude",
        "practices": [
            "Release ceremony to let go of what no longer serves",
            "Bathe in moonlight (moonbathing)",
            "Meditate on completion and gratitude",
            "Journal about lessons learned this lunar cycle",
            "Practice forgiveness rituals",
            "Celebrate achievements and milestones"
        ],
        "affirmations": [
            "I release all that holds me back",
            "I am grateful for all I have learned",
            "I celebrate my growth and transformation"
        ],
        "ritual": "Write down what you're releasing on paper, safely burn it, bathe in moonlight, meditate on letting go with gratitude."
    }
}

# ============================================================================
# FESTIVAL GUIDES (Celebrate Indian Festivals Mindfully)
# ============================================================================
festival_guides = [
    {
        "festival": "Diwali (Festival of Lights)",
        "month": "October/November",
        "significance": "Victory of light over darkness, inner illumination, celebration of consciousness",
        "mindful_practices": [
            "Light lamps with intention, visualizing inner light awakening",
            "Clean your space symbolizing mental purification",
            "Give gifts with love, spreading joy to others",
            "Meditate on the light within you for 30 minutes",
            "Perform gratitude rituals for blessings received",
            "Share sweets mindfully, spreading sweetness in relationships"
        ],
        "affirmation": "My inner light shines brightly. I am the light I seek.",
        "significance_deep": "Diwali represents the triumph of good over evil, light over darkness, knowledge over ignorance. It's a celebration of your inner illumination."
    },
    {
        "festival": "Holi (Festival of Colors)",
        "month": "March",
        "significance": "Love, playfulness, renewal, forgiveness, harmony",
        "mindful_practices": [
            "Use natural colors and play mindfully, with intention",
            "Forgive those who hurt you; seek forgiveness from others",
            "Start fresh relationships with love and joy",
            "Cleanse your mind of negativity and grudges",
            "Celebrate diversity and unity in colors",
            "Share laughter and joy without attachment"
        ],
        "affirmation": "I celebrate color, love, and forgiveness. My heart is light and joyful.",
        "significance_deep": "Holi teaches that relationships matter more than pride, that forgiveness heals, and that life's diversity is beautiful."
    },
    {
        "festival": "Navaratri (Nine Nights of the Divine Feminine)",
        "month": "September/October",
        "significance": "Honoring the divine feminine, inner strength, triumph of good, transformation",
        "mindful_practices": [
            "Meditate on Durga Shakti—your inner strength and power",
            "Practice goddess poses in yoga (Warrior poses)",
            "Chant Devi Mahatmya or Devi Sukta mantras",
            "Honor the women in your life",
            "Fast mindfully for purification (if comfortable)",
            "Dance (Garba or Dandiya) with joy and community"
        ],
        "affirmation": "I honor my inner strength. The divine feminine flows through me.",
        "significance_deep": "Navaratri celebrates the 9 forms of Shakti, the primordial feminine energy. Each day represents a different aspect of your inner strength."
    },
    {
        "festival": "Makar Sankranti (Winter Solstice Transition)",
        "month": "January",
        "significance": "New solar year, transition, harvest, gratitude, change",
        "mindful_practices": [
            "Bathe in morning sun, absorbing new energy",
            "Fly kites mindfully, symbolizing letting go of limitations",
            "Share sesame and jaggery, symbolizing sweetness in relationships",
            "Practice sun salutations (Surya Namaskar) with devotion",
            "Set intentions for the new cycle",
            "Give to those in need, spreading abundance"
        ],
        "affirmation": "I welcome new beginnings with open arms. I am grateful for all transitions.",
        "significance_deep": "Makar Sankranti marks the sun's transition into Capricorn. It's about moving from darkness to light, from winter to spring."
    },
    {
        "festival": "Rakhi (Bond of Protection)",
        "month": "August",
        "significance": "Protection, unconditional love, sibling bonds, mutual care",
        "mindful_practices": [
            "Express gratitude to those who protect you",
            "Renew bonds of love and responsibility",
            "Practice mudras for protection and strength",
            "Meditate on unconditional love and care",
            "Offer service to those you love",
            "Exchange blessings with loved ones"
        ],
        "affirmation": "I am protected. I protect and nurture those I love.",
        "significance_deep": "Rakhi celebrates the sacred bond between siblings and loved ones, emphasizing mutual protection and unconditional love."
    },
    {
        "festival": "Janmashtami (Birth of Krishna)",
        "month": "August/September",
        "significance": "Divine incarnation, playfulness, devotion, surrender, spiritual wisdom",
        "mindful_practices": [
            "Meditate on Krishna's teachings in Bhagavad Gita",
            "Practice devotional chanting of Krishna mantras",
            "Sing bhajans (devotional songs) with full heart",
            "Celebrate divine playfulness (Lila) in your life",
            "Practice surrender and trust in divine plan",
            "Distribute sweets mindfully, spreading joy"
        ],
        "affirmation": "I trust the divine plan. My life is a divine play unfolding perfectly.",
        "significance_deep": "Janmashtami celebrates the birth of Krishna, the embodiment of divine love, wisdom, and playfulness."
    },
    {
        "festival": "Mahashivaratri (Night of Shiva)",
        "month": "February/March",
        "significance": "Meditation, transformation, destruction of ego, spiritual awakening",
        "mindful_practices": [
            "Meditate through the night if possible",
            "Chant Om Namah Shivaya 108 times or more",
            "Fast for purification (if comfortable)",
            "Practice Shiva mudra and advanced meditation",
            "Contemplate the cycle of creation, maintenance, and destruction",
            "Release ego and attachments"
        ],
        "affirmation": "I dissolve my ego. I am transformed. I am one with the eternal consciousness.",
        "significance_deep": "Mahashivaratri honors Shiva, the destroyer of ignorance. It's about transcending the ego and experiencing unity consciousness."
    }
]

# ============================================================================
# COMPREHENSIVE WISDOM QUOTES (diverse & beautiful)
# ============================================================================
wisdom_quotes = [
    "In a gentle way, you can shake the world. — Mahatma Gandhi",
    "Compassion is the fragrance of the soul. — Swami Vivekananda",
    "The only true wisdom is in knowing you know nothing. — Socrates",
    "Peace comes from within. Do not seek it without. — Buddha",
    "Be the change you wish to see in the world. — Mahatma Gandhi",
    "You yourself, as much as anybody in the entire universe, deserve your love and affection. — Buddha",
    "The purpose of our lives is to be happy. — Dalai Lama",
    "Happiness is not by chance, but by choice. — Jim Rohn",
    "Do not dwell in the past, do not dream of the future, concentrate the mind on the present moment. — Buddha",
    "The greatest glory in living lies not in never falling, but in rising every time we fall. — Nelson Mandela",
    "Begin where you are.",
    "Breathe before you react.",
    "Small steps still move you forward.",
    "Peace starts with awareness.",
    "Let today unfold gently.",
    "You are allowed to slow down.",
    "Choose calm over noise.",
    "Notice what is already enough.",
    "Presence is power.",
    "One mindful breath changes the moment.",
    "Clarity comes from stillness.",
    "You don’t need to rush.",
    "Today is not a race.",
    "Respond with kindness.",
    "Be here fully.",
    "Let go of what you cannot control.",
    "Silence can heal.",
    "Progress is not always loud.",
    "Rest is also productive.",
    "Trust the timing of your life.",
    "Listen more than you speak.",
    "Your breath is an anchor.",
    "Peace is a daily practice.",
    "Focus on what truly matters.",
    "Let your mind soften.",
    "You are doing better than you think.",
    "Patience creates space.",
    "Calm is a choice.",
    "Release unnecessary tension.",
    "Be gentle with yourself.",
    "Clarity grows in quiet moments.",
    "Nothing needs to be forced today.",
    "Observe before judging.",
    "Slow moments hold wisdom.",
    "Your energy matters.",
    "Inner peace is strength.",
    "Choose simplicity.",
    "Awareness is freedom.",
    "One step at a time.",
    "Stillness restores balance.",
    "Kindness begins within.",
    "Pause. Then proceed.",
    "Let today be light.",
    "Not everything needs a response.",
    "Peace does not require perfection.",
    "Stay rooted in the present.",
    "Calm is contagious.",
    "Less effort, more awareness.",
    "Your pace is valid.",
    "Notice the space between thoughts.",
    "Softness is not weakness.",
    "Allow things to be as they are.",
    "Balance comes from within.",
    "Today deserves your attention.",
    "Breathe into the moment.",
    "Trust small beginnings.",
    "Let go, gently.",
    "Quiet strength lasts longer.",
    "Inner calm shapes outer life.",
    "One mindful choice is enough.",
    "Choose clarity over confusion.",
    "Be patient with the process.",
    "Awareness brings ease.",
    "Peace is already available.",
    "Move with intention.",
    "Your breath knows the way.",
    "Release what drains you.",
    "Stillness speaks.",
    "Let presence guide you.",
    "Calm supports clarity.",
    "Ease into the day.",
    "Accept what is.",
    "Let thoughts pass.",
    "Presence changes perspective.",
    "Choose depth over speed.",
    "Peace grows quietly.",
    "Allow space for rest.",
    "Trust yourself more.",
    "Attention is sacred.",
    "Calm brings insight.",
    "Today does not need fixing.",
    "Return to your breath.",
    "Soft focus reveals truth.",
    "Inner quiet is powerful.",
    "Observe without attachment.",
    "Let calm lead.",
    "Nothing is missing right now.",
    "Be steady.",
    "Stillness sharpens awareness.",
    "Clarity lives here.",
    "Choose mindful action.",
    "Let ease replace effort.",
    "Your breath is enough.",
    "Peace comes from acceptance.",
    "Be present, gently.",
    "Slow clarity is real clarity.",
    "Let awareness expand.",
    "Pause invites wisdom.",
    "Inner balance matters.",
    "Stay with the moment.",
    "Calm settles the mind.",
    "Be kind to your pace.",
    "Presence simplifies everything.",
    "Release mental noise.",
    "Quiet attention transforms.",
    "Trust your inner rhythm.",
    "Choose stillness when unsure.",
    "Awareness dissolves tension.",
    "Nothing needs rushing.",
    "Be rooted, not reactive.",
    "Peace thrives in simplicity.",
    "Let the mind rest.",
    "Stay open.",
    "Calm reveals what matters.",
    "Allow gentle focus.",
    "Choose awareness today.",
    "Be steady in breath.",
    "Inner peace builds resilience.",
    "Let calm arrive naturally.",
    "Stay grounded.",
    "Notice without judging.",
    "Peace lives in attention.",
    "Soft moments matter.",
    "Ease is allowed.",
    "Choose clarity.",
    "Return to center.",
    "Let life breathe.",
    "Be aware, not anxious.",
    "Stillness brings insight.",
    "Calm guides wise action.",
    "Today is enough.",
    "Let go of excess effort.",
    "Rest the mind.",
    "Peace begins inside.",
    "Trust quiet confidence.",
    "Be calm, be clear.",
    "Awareness shapes experience.",
    "Slow is sustainable.",
    "Stay attentive.",
    "Release inner pressure.",
    "Calm holds strength.",
    "Nothing urgent right now.",
    "Let breath lead.",
    "Choose presence.",
    "Peace follows acceptance.",
    "Be here, fully.",
    "Quiet focus sharpens clarity.",
    "Allow balance.",
    "Stay soft inside.",
    "Calm creates space.",
    "Observe with compassion.",
    "Trust simplicity.",
    "Let the day be light.",
    "Inner stillness supports action.",
    "Awareness reduces struggle.",
    "Move gently.",
    "Choose calm awareness.",
    "Peace grows with practice.",
    "Let the mind settle.",
    "Notice what remains.",
    "Be patient with thoughts.",
    "Clarity does not hurry.",
    "Rest in awareness.",
    "Calm steadies decisions.",
    "Be grounded in now.",
    "Let go slowly.",
    "Peace welcomes you.",
    "Stay mindful.",
    "Soft attention heals.",
    "Nothing to prove today.",
    "Calm opens perspective.",
    "Allow the moment.",
    "Trust presence.",
    "Be attentive.",
    "Inner quiet strengthens resolve.",
    "Ease replaces force.",
    "Peace lives here.",
    "Choose mindful ease.",
    "Let awareness guide action.",
    "Stay calm within.",
    "Presence clarifies intention.",
    "Nothing extra needed.",
    "Be gentle with effort.",
    "Calm restores balance.",
    "Stay centered.",
    "Quiet wisdom emerges.",
    "Trust inner calm.",
    "Observe patiently.",
    "Peace deepens over time.",
    "Choose simplicity again.",
    "Let attention rest.",
    "Be calm in movement.",
    "Awareness softens stress.",
    "Stay steady.",
    "Clarity through calm.",
    "Let breath steady you.",
    "Peace is practical.",
    "Notice calm moments.",
    "Trust the pause.",
    "Be aware today.",
    "Inner stillness supports growth.",
    "Ease into clarity.",
    "Calm is grounding.",
    "Stay open to quiet.",
    "Nothing to force.",
    "Presence nurtures peace.",
    "Let go of hurry.",
    "Choose mindful focus.",
    "Be relaxed and alert.",
    "Calm brings understanding.",
    "Trust gentle effort.",
    "Peace is sustainable.",
    "Stay with awareness.",
    "Quiet moments guide.",
    "Let calm shape action.",
    "Be attentive now.",
    "Clarity lives in stillness.",
    "Allow ease.",
    "Peace responds to attention.",
    "Choose grounded calm.",
    "Be centered.",
    "Inner quiet is clarity.",
    "Trust steady progress.",
    "Observe calmly.",
    "Peace comes naturally.",
    "Let focus soften.",
    "Stay balanced.",
    "Calm supports insight.",
    "Be aware of breath.",
    "Nothing to chase.",
    "Presence simplifies life.",
    "Choose still awareness.",
    "Let calm deepen.",
    "Be quietly confident.",
    "Peace begins again.",
    "Stay mindful of now.",
    "Ease creates flow.",
    "Clarity through patience.",
    "Trust gentle awareness.",
    "Be steady today.",
    "Calm brings order.",
    "Observe with kindness.",
    "Peace settles naturally.",
    "Let awareness widen.",
    "Stay grounded in breath.",
    "Choose calm clarity.",
    "Be present gently.",
    "Inner balance is power.",
    "Trust simplicity daily.",
    "Peace grows steadily.",
    "Let the mind rest again.",
    "Be calmly focused.",
    "Awareness reduces noise.",
    "Stay centered today.",
    "Quiet presence heals.",
    "Choose patient awareness.",
    "Let calm guide you.",
    "Be steady and kind.",
    "Peace feels natural.",
    "Stay attentive and calm.",
    "Ease supports clarity.",
    "Trust inner stillness."
]

daily_actions = [
    "Meditate for 10 minutes",
    "Practice gratitude for 3 things",
    "Move your body mindfully",
    "Drink water and stay hydrated",
    "Read something inspiring",
    "Practice deep breathing for 5 minutes",
    "Do a kind act for someone",
    "Journal about your day",
    "Practice mindful eating",
    "Spend time in nature",
]

bhagavad_gita_verses = [
    "You have the right to work, but never to the fruit of work. — Bhagavad Gita 2.47",
    "Yoga is the journey of the self, through the self, to the self. — Bhagavad Gita 6.20",
    "A person is said to have achieved yoga, the union with the Self, when the perfectly disciplined mind gets absorbed in the infinite. — Bhagavad Gita 6.23",
    "The soul is never born, and nor does it die. — Bhagavad Gita 2.20",
    "Change is the only constant in life. — Bhagavad Gita",
    "It is better to live your own destiny imperfectly than to live an imitation of somebody else's life with perfection. — Bhagavad Gita 3.35",
]
# ... (keep all other existing functions and content)

# ============================================================================
# NEW ROUTES FOR MYTHOLOGY, MANTRAS, RITUALS, ETC.
# ============================================================================

@app.route("/mantras")
def mantras():
    """Display Sanskrit mantras with pronunciation and meanings"""
    mantra = random.choice(sanskrit_mantras)
    return render_template("mantras.html", mantras=sanskrit_mantras, featured_mantra=mantra)

@app.route("/rituals")
def rituals():
    """Display Vedic rituals for daily wellness"""
    ritual = random.choice(vedic_rituals)
    return render_template("rituals.html", rituals=vedic_rituals, featured_ritual=ritual)


@app.route("/api/mantra")
def api_mantra():
    """API endpoint for random mantra"""
    return jsonify(random.choice(sanskrit_mantras))

@app.route("/api/ritual")
def api_ritual():
    """API endpoint for random vedic ritual"""
    return jsonify(random.choice(vedic_rituals))

@app.route("/")
def home():
    """Display home page"""
    daily_content = {
        "quote": random.choice(wisdom_quotes),
        "action": random.choice(daily_actions),
        "bhagavad_gita": random.choice(bhagavad_gita_verses),
        "tip": "Start your day with gratitude. It shifts your vibration instantly."
    }
    return render_template("home.html", month_themes=month_themes, daily_content=daily_content)

@app.route("/calendar")
def calendar_view():
    today = datetime.date.today()
    year = today.year

    month = request.args.get(
        "month",
        default=today.month,
        type=int
    )

    weeks = pycalendar.monthcalendar(year, month)
    month_name = pycalendar.month_name[month]
    theme = month_themes.get(month, "Mindfulness")

    mapping = {}

    for week in weeks:
        for day in week:
            if day == 0:
                continue

            date_obj = datetime.date(year, month, day)

            # 🔑 THIS IS THE KEY LINE
            day_of_year = date_obj.timetuple().tm_yday  # 1–365/366

            quote_index = (day_of_year - 1) % len(wisdom_quotes)

            mapping[day] = {
                "quote": wisdom_quotes[quote_index],
                "action": daily_actions[quote_index % len(daily_actions)]
            }

    return render_template(
        "calendar.html",
        weeks=weeks,
        month=month,
        month_name=month_name,
        year=year,
        theme=theme,
        month_themes=month_themes,
        mapping=mapping
    )


@app.route("/emotions")
def emotions():
    """Display emotions page"""
    return render_template("emotions.html")

@app.route("/ideas")
def ideas():
    """Display ideas page"""
    return render_template("ideas.html")

@app.route("/stress")
def stress():
    """Display stress relief page"""
    return render_template("stress.html")

@app.route("/about")
def about():
    """Display about page"""
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
# ... (keep all existing routes and error handling)