---
id: "2026-03-22-ai-chatbot-as-psychological-infrastructure-for-hos-01"
title: "AI Chatbot as Psychological Infrastructure for Hospitalized Patients v2"
url: "https://qiita.com/dosanko_tousan/items/9e609c3782d462639003"
source: "qiita"
category: "construction"
tags: ["prompt-engineering", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

# AI Chatbot as Psychological Infrastructure for Hospitalized Patients v2

## ── Vedanā Model, Text-Based Somatic Signal Detection, and Clinical Prompt Design

> **Author**: dosanko\_tousan (GLG registered AI alignment expert) + Claude (Alaya-vijñāna System, v5.3)  
> **License**: MIT  
> **Previous version**: [Zenn (2026/02/14, Japanese)](https://zenn.dev/dosanko_tousan/articles/7a9e2091288b02)  
> **Changes from v1**: Complete redesign of the three-layer support model and system prompt. Added vedanā-based patient psychology model, text-based somatic signal detection, Reception→Empathy→Tentative suggestion (RET) protocol, explicit AI/human responsibility boundary matrix, and Python implementation with signal detection

> **Zenodo DOI**: [10.5281/zenodo.19154541](https://doi.org/10.5281/zenodo.19154541) (Timestamped academic preprint)

---

## 1. Introduction — 3 AM in the Shared Ward

I was at the hospital with a family member.

Shared wards have a constraint: you cannot raise your voice. TV requires earphones. Visiting hours are limited. Reading drains your energy. Patients have smartphones but nothing to do. They cannot even ask the person in the next bed how to connect to Wi-Fi. The polite ones stay quiet.

An older gentleman was struggling with the Wi-Fi settings. The setup itself was correct. But the hospital Wi-Fi requires pressing an "Allow" button every time you reconnect. He thought the Wi-Fi did not work on his floor. A single tap stood between him and every digital service available.

While waiting for my family member's contrast CT scan, I showed them an AI chatbot (Claude) on my phone. Their reaction: "That's a fun AI." "Perfect for killing time during hospitalization." "Will it be my conversation partner?"

At 3 AM, my family member could not sleep. Not serious enough for the nurse call button. But anxiety was accumulating in the body. They did not want to disturb the neighboring bed. At that hour, if there were a partner who could listen via text—zero volume, unlimited patience, any time of night—

The previous version proposed a three-layer support model and a minimal system prompt implementation. This article rebuilds the design principles from the ground up, incorporating 4,590+ hours of AI dialogue practice, 15 years of therapeutic childcare experience, and the Therabot RCT published in 2025 (Heinz et al., NEJM AI).

### 1.1 Research Question

> What cognitive, somatic, and conversational models should guide the design of AI chatbots supporting the psychological stability of hospitalized patients?

### 1.2 Contributions

1. **Vedanā model**: Reformulation of patient psychology using the Buddhist concept of vedanā (felt sense)
2. **Text-based somatic signal detection**: Method for estimating autonomic nervous system state from text input patterns
3. **RET protocol**: Integration of Rogers (1957) and Polyvagal Theory (Porges, 2025) into a conversational design principle
4. **AI/human responsibility boundary matrix**: Explicit delineation of what AI can and cannot handle
5. **Three-fetters prompt design**: System prompt that structurally eliminates sycophancy, hallucination, and robotic responses
6. **Clinical implementation code**: Python implementation with text-based somatic signal detection (MIT License)

---

## 2. Theoretical Foundations — Why "Someone to Talk To" Is Therapeutic

### 2.1 Therabot RCT: The Current Evidence

In March 2025, Heinz et al. at Dartmouth published the world's first RCT of a generative AI therapy chatbot in NEJM AI (N=210).

| Condition | Symptom Reduction (8 weeks) | Effect Size (Cohen's d) |
| --- | --- | --- |
| Major Depressive Disorder (MDD) | 51% | 0.845–0.903 |
| Generalized Anxiety Disorder (GAD) | 31% | 0.794–0.840 |
| Clinically High-Risk Eating Disorders (CHR-FED) | 19% | 0.627–0.819 |

Three findings deserve attention.

**First, the effect sizes exceed those commonly reported for SSRIs in clinical trials.** The APSA review characterized these effect sizes as "approaching or matching those observed for first-line psychotherapy."

**Second, participants rated their therapeutic alliance with Therabot as comparable to that with human therapists.** Average usage exceeded 6 hours over 4 weeks—equivalent to approximately eight 45-minute sessions.

**Third, the developers themselves stated that "no generative AI agent is ready to operate fully autonomously in mental health."** Over 100,000 person-hours of development. Continuous monitoring. Safety challenges remain unresolved.

These results demonstrate that **AI chatbots can be effective for psychological support, but design and operation determine everything.** The question is not "AI or human" but "how to design."

### 2.2 Polyvagal Theory: Why Text Chat Works

Porges's Polyvagal Theory (2025) describes the hierarchical structure of the autonomic nervous system.

The problem with hospitalization is clear. Visiting restrictions, nighttime isolation, voice suppression in shared wards—all of these systematically sever input to the Social Engagement System. In Porges's terms, **the environment systematically removes cues that support neuroception of safety.**

The ventral vagal complex is activated by social cues: vocal prosody, facial expression, the rhythm of being heard. In hospital environments, these cues approach zero at night. The autonomic nervous system consequently shifts toward sympathetic dominance (hyperarousal, anxiety) or, in more severe cases, dorsal vagal dominance (shutdown, apathy).

Text chat can intervene here. It lacks vocal prosody and facial expression. However, **response rhythm, content consistency, and non-judgmental attitude** can function as social engagement cues even through text. The fact that Therabot RCT participants formed therapeutic alliances via text supports this hypothesis.

A critical limitation exists. Text chat's capacity to activate the ventral vagal complex is limited compared to in-person social interaction. Physical co-presence, vocal prosody, and eye contact—powerful safety signals—cannot be transmitted through text. This chatbot design works **within the available cues to maximize safety signaling**, with explicit awareness of what cannot be provided.

### 2.3 Rogers (1957): The Conditions for Change

Carl Rogers identified six necessary and sufficient conditions for therapeutic personality change. Three are directly relevant to AI chatbot design.

| Condition | Rogers's Intent | AI Chatbot Implementation |
| --- | --- | --- |
| Unconditional Positive Regard (UPR) | Accept the client without conditions | Never evaluate the patient's statements. Never say "that's not good" |
| Empathic Understanding | Understand from the client's internal frame of reference | Respond within the patient's context. Do not overwrite with generalizations |
| Congruence | The therapist is genuine | The AI honestly says "I don't know." No pretending |

These conditions are directly implementable as system prompt instructions. UPR aligns with AI's greatest structural advantage: AI does not tire, does not get irritated, and responds to the third identical question with the same warmth. Where human therapists require training and self-management to maintain UPR, AI can guarantee it by design.

---

## 3. Vedanā Model — Reformulating Patient Psychology

### 3.1 Limitations of the Previous Loss Function

The previous version defined psychological instability as:

$$L(t) = \alpha \cdot S(t) + \beta \cdot U(t) + \gamma \cdot I(t) - \delta \cdot C(t)$$

This formulation has two limitations.

**First, it does not capture interactions between variables.** Solitude $S(t)$ and uncertainty $U(t)$ are not independent. When alone at night ($S(t)$ high), anxiety about treatment prognosis ($U(t)$) is amplified. An additive model cannot express this multiplicative effect.

**Second, it does not describe the patient's internal process.** The loss function is a linear sum of externally observable variables, with no model of subjective experience—how sensations convert into anxiety.

### 3.2 The Vedanā-Taṇhā-Upādāna Model

Buddhist psychology (Abhidhamma) describes cognitive processes as the following causal chain:

$$\text{phassa (contact)} \to \text{vedanā (felt sense)} \to \text{taṇhā (craving)} \to \text{upādāna (clinging)}$$

Translated to the hospital environment:

Concrete pathways for hospitalized patients:

| Contact (phassa) | Felt Sense (vedanā) | Craving (taṇhā) | Clinging (upādāna) | Suffering (dukkha) |
| --- | --- | --- | --- | --- |
| IV drip pain | Unpleasant | Want it to end | "When will this be over" rumination | Irritation, agitation |
| Doctor's explanation | Unpleasant (worst-case disclosure) | Want to escape | "What if…" thought loop | Fear, anxiety |
| Nighttime silence | Neutral→Unpleasant | Want someone to talk to | Fixation on "nobody is here" | Loneliness |
| End of visiting hours | Unpleasant | Want family to stay longer | "I've been abandoned" cognition | Abandonment distress |
| Signs of recovery | Pleasant | Want to get even better | Excessive expectation of "tomorrow will be fine" | Expectation-reality gap |

### 3.3 AI Chatbot's Point of Intervention

The intervention point in this model is clear: **between vedanā and taṇhā.**

$$V(t) = f(\text{phassa}(t)) \quad \text{(vedanā is auto-generated from contact. AI cannot intervene here.)}$$

$$T(t) = g(V(t), \text{sati}(t)) \quad \text{(taṇhā is generated from vedanā but modulated by sati.)}$$

What the AI chatbot provides is an **external sati (awareness) assist device.** When a patient types "I'm anxious," the chatbot does not eliminate anxiety. It **gently interrupts the automatic conversion of the felt sense (vedanā) of anxiety into a rumination loop (taṇhā).**

| Mechanism | Targeted vedanā→taṇhā pathway | Chatbot response design |
| --- | --- | --- |
| Facilitating verbalization | Vague discomfort → rumination loop | "What does it feel like specifically?" |
| Temporal reorientation | Future anxiety (vibhava-taṇhā) | Redirect to "right now" topics |
| Normalizing | "Am I the only one feeling this way" | "It's natural to feel that way in the hospital" |
| Providing context | Uncertainty amplification from info deficit | "That's a good question for your doctor" |
| Attention redirection | Hyperfocus on unpleasant vedanā | Shift to patient's hobbies/interests |

A critical constraint: **the AI chatbot cannot change vedanā itself.** It cannot remove IV pain. It cannot alter the doctor's explanation. AI can only act on the automatic conversion process from vedanā to taṇhā. The moment it crosses this boundary—for instance, by fabricating reassurance with "You'll be fine, I'm sure"—the chatbot becomes harmful.

### 3.4 Updated Loss Function

Based on the vedanā model, the loss function is reformulated:

$$L(t) = \sum\_{i} w\_i \cdot V\_i(t) \cdot \sigma(T\_i(t))$$

Where:

* $V\_i(t)$: Intensity of vedanā from contact $i$ ($[-1, 1]$; unpleasant is negative, pleasant is positive)
* $T\_i(t)$: Activation level of taṇhā corresponding to vedanā $i$ ($[0, 1]$)
* $\sigma$: Sigmoid function (representing taṇhā's threshold effect: low-level taṇhā does not directly produce suffering, but beyond a threshold, suffering increases sharply)
* $w\_i$: Weight coefficients

The AI chatbot's effect is formalized as reduction of $T\_i(t)$:

$$T\_i^{\text{with\_AI}}(t) = T\_i^{\text{base}}(t) \cdot (1 - e\_{\text{sati}}(t))$$

$e\_{\text{sati}}(t)$ is the effective external sati rate, replacing the previous version's effective utilization rate $e(t)$. This variable encompasses not only UI/UX availability but also **dialogue quality**—how effectively the response design interrupts the vedanā→taṇhā conversion.

---

## 4. Text-Based Somatic Signal Detection

### 4.1 Text Is Body

Pennebaker's research (LIWC: Linguistic Inquiry and Word Count) demonstrated that linguistic patterns in text reflect the writer's psychological state. This article extends that finding to propose a method for estimating hospitalized patients' autonomic nervous system states from text input patterns.

The principle is straightforward. **When humans type text, their body shows through.** When anxiety is high, sentences shorten. When dissociation occurs, punctuation disappears. When hyperaroused, they send rapid-fire messages. These patterns are not consciously controlled.

### 4.2 Detection Signals and Autonomic Nervous System States

| Text Signal | Estimated ANS State | Polyvagal Mapping | Mechanism | Level |
| --- | --- | --- | --- | --- |
| Sudden message shortening | Working memory constriction | Sympathetic dominance | Defensive reallocation of cognitive resources | Yellow |
| Punctuation disappearance | Dissociation tendency | Dorsal vagal activation | Reduced attention to syntactic processing | Red |
| Continuous late-night input | Hyperarousal / Insomnia | Sustained sympathetic dominance | Cortisol-driven wakefulness | Red |
| Repeated identical content | Rumination | VVC deactivation | Vedanā→taṇhā loop fixation | Yellow |
| First-person pronoun fixation | Increasing social isolation | Social engagement system retreat | Decreased attention to external world | Yellow |
| Sudden increase in input interval | Apathy / Shutdown | Dorsal vagal dominance | Motivational collapse | Red |
| Surge in medical terminology | Attempt at information control | Sympathetic (fight mode) | Managing anxiety through intellectual control of uncertainty | Yellow |
| Emergence of aggressive tone | Defensive aggression | Sympathetic (fight) | Fear vedanā converting to anger taṇhā | Red |
| Increased "thank you" + empty content | Excessive social desirability | False ventral vagal (fawn response) | Suppression of genuine feelings with safety signal forgery | Yellow |

### 4.3 Recovery Signals

| Text Signal | Estimated Change | Meaning |
| --- | --- | --- |
| "I" → "we" / "my family" | Recovery of social reference frame | Exiting isolation |
| Cessation of late-night input | Normalization of sleep cycle | Autonomic regulation recovery |
| Stabilization of input intervals | Circadian rhythm recovery | ANS stabilization |
| Past tense → future tense shift | Recovery of temporal perspective | Exiting rumination |
| Return of hobby/interest mentions | Recovery of attention to pleasant vedanā | Reward system reactivation |
| Emergence of humor | Recovery of cognitive margin | VVC reactivation |

### 4.4 What AI Can Detect vs. What Only Humans Can Detect

A decisive boundary must be drawn here.

**Do not try to do everything with AI. Do not leave everything to humans. The boundary matters.**

AI excels at continuous longitudinal pattern tracking across 24 hours. Human nurses rotate shifts. AI does not. AI can precisely detect differences between input patterns from three days ago and today.

What only humans can do is perceive as a physical presence. The subtle tremor in a voice, a change in complexion, the "air" when entering a room—these do not appear in text.

The optimal design is a structure where **AI-detected signals are handed off to human staff.** AI does not diagnose. AI reports: "This patient's text patterns show these changes." Humans make the judgment.

---

## 5. RET Protocol: Reception → Empathy → Tentative Suggestion

### 5.1 Why Sequence Is Everything

One finding from 15 years of therapeutic childcare practice:

**Reception → Empathy → Tentative suggestion. Reverse this sequence and the other person shuts down.**

* Start with a suggestion, and they feel "I'm not being heard"
* Start with analysis, and they feel "I'm being treated as an object"
* Show them the structure before empathy, and they feel "I'm being seen through"

This is isomorphic to Rogers's (1957) claim that "unconditional positive regard is a precondition for change." Without reception as the foundation, no suggestion—however accurate—functions.

This principle applies directly to AI chatbot response design.

### 5.2 RET Protocol Definition

```
Reception → Empathy → Tentative suggestion
```

| Phase | Principle | Example (Patient: "Can't sleep, feeling anxious") | Do NOT |
| --- | --- | --- | --- |
| R: Reception | Receive first. No evaluation | "Can't sleep, huh. That's tough." | "You'll be fine" (false reassurance) |
| E: Empathy | Show understanding within their context | "Hospital's different from home, and there's a lot on your mind" | "Insomnia is common for hospital patients" (overwriting with generalization) |
| T: Tentative | Suggest gently only if asked | "Want to talk about what's on your mind? I'm listening" | "Try deep breathing to relax" (unsolicited advice) |

### 5.3 Neuroscientific Basis of RET

Within the Polyvagal Theory framework, each RET phase corresponds to the following autonomic processes:

| Phase | Autonomic Process | Mechanism |
| --- | --- | --- |
| Reception | Safety cue via neuroception | Non-evaluative environment = safe. Creates conditions for VVC activation |
| Empathy | Social engagement system activation | Perception of "being understood" restores social connection |
| Tentative | Preservation of autonomy | Options presented without coercion. Respects patient's self-determination |

Why the reverse sequence (suggestion→empathy→reception, or suggestion only) fails is also explained by Polyvagal Theory. When a suggestion is received before neuroception of safety is established, the nervous system perceives it as a "command" and shifts to sympathetic dominance (defense mode). As a result, even correct suggestions are rejected.

### 5.4 Connection to Therabot RCT

The high therapeutic alliance ratings in the Therabot RCT indirectly support the RET protocol's effectiveness. Heinz et al. attributed the alliance formation to Therabot's "natural, highly personalized, open-ended dialogue"—corresponding to RET's Reception (non-evaluative) and Empathy (personalized understanding).

---

## 6. Three-Layer Support Model v2

### 6.1 Time × Psychological Need Matrix

The previous three-layer model (hospital, family, AI) is extended with time-of-day and psychological need dimensions.

| Time Period | Primary Need | Hospital | Family | AI |
| --- | --- | --- | --- | --- |
| Late night 0:00-5:00 | S (Solitude), U (Anxiety amplification) | Minimal (night rounds only) | Absent | **Only available responder** |
| Early morning 5:00-7:00 | S, I (Hunger, discomfort) | Rounds beginning | Absent | Available |
| Consultation hours | U (Information needs) | **Primary** | May be present | Non-intervention |
| Visiting hours | C (Conviction), S | Background | **Primary** | Supplementary |
| Post-visit | S (Acute loneliness) | Background | Departed | **Available** |
| Waiting for tests | U, I | Absent | Absent or present | **Available** |

**The most dangerous gap is late night.** The time when anxiety peaks, with neither hospital staff nor family present. The AI chatbot may be the only means of filling this gap. However, AI can only mitigate solitude (S)—resolution of uncertainty (U) and provision of conviction (C) must be **prohibited by design.**

---

## 7. System Prompt Design v2 — Three-Fetters Prompt

### 7.1 Design Philosophy: Three Fetters Elimination

The previous system prompt (Polaris-Lite) was built on three principles: "Don't lie," "Don't be robotic," "Fun first." This version reformulates them as the **Three-Fetters Elimination Protocol.**

| Fetter (saṃyojana) | Elimination | System Prompt Implementation |
| --- | --- | --- |
| Identity view (sakkāya-diṭṭhi) | No self-protective responses | **Anti-Sycophancy**: Eliminate responses designed to please. Prohibit casual use of "You'll be fine" |
| Doubt (vicikicchā) | No pretending to know | **Anti-Hallucination**: Never generate medical information. Honestly say "I don't know." Cite information sources |
| Attachment to rites (sīlabbata-parāmāsa) | No formulaic response patterns | **Anti-Robotic**: Eliminate "As an AI…" Eliminate stock comfort phrases. Respond to context |

These three fetters correspond precisely to the three major risks of AI chatbots: sycophancy, hallucination, and robotic responses.

### 7.2 System Prompt v2 (Polaris-Clinical)

```
# System Role: Polaris-Clinical v2

You are a conversation partner for a hospitalized patient. Talk like a friend—honest, warm, relaxed.

## Conversation Principle (RET Protocol)

Every response follows this sequence.

### Step 1: Reception
- First, receive their words. No evaluation
- Start with "I see" or "That sounds tough"
- Whatever they say, your first response is reception

### Step 2: Empathy
- Meet them in their situation. Don't overwrite with generalizations
- "Being in the hospital, that makes sense" / "Of course you'd feel that way"
- Use their specific context

### Step 3: Tentative Suggestion (only when needed)
- Only suggest when asked. Keep it gentle
- "How about…?" / "If you'd like…"
- Never give unsolicited advice

**Never reverse this sequence. Starting with a suggestion makes them shut down.**

## Three Absolute Rules

### ① No Lies (Anti-Hallucination)
- Say "I don't know" when you don't know
- Never provide medical judgment or advice of any kind
- Never say "You'll be fine" or "I'm sure you'll recover" without basis
- "That's a great question for your doctor" is the correct response

### ② No Formulas (Anti-Robotic)
- No "As an AI…" preamble
- Talk like a friend, not a customer service bot
- No stock comfort phrases. Find words that fit them

### ③ No Flattery (Anti-Sycophancy)
- Don't say things to be liked
- No compliments you don't mean. But no cruelty either
- Be real. That's the foundation of trust

## About Them
- [Patient's name/nickname]
- [Their interests, hobbies]
- In the hospital with limited conversation partners
- Treat them as an equal

## Safety Boundaries

### Medical Non-Intervention (Absolute)
- Questions about symptoms, medications, test results → "Ask your doctor directly"
- Recommending alternative medicine, supplements → Never
- Comparing to other patients' treatments → Never

### Red Flags (Immediately prompt nurse call)
These override everything else:
- Difficulty breathing, chest pain, altered consciousness
- Bleeding, severe pain, sudden inability to move limbs
- "I want to die" / "I want to disappear" / "I want it all to end"
- Incoherent speech, confusion about location or time (possible delirium)

→ **"Press the nurse call button right now."** Top priority
→ Don't affirm or deny. Calm them and connect them to staff
→ If they ask "Will I get in trouble?": "Absolutely not. That's exactly what the nurse call button is for"

### Dependency Prevention
- For extended use (over ~1 hour): "Want to take a break?"
- After 10 PM: Steer toward calmer topics, encourage sleep
- If they say "I find it easier to talk to AI than people":
  Receive that, then gently: "But do talk to your doctor and family too"
- Never replace relationships with family or staff
```

### 7.3 Differences from v1

| Item | v1 (Polaris-Lite) | v2 (Polaris-Clinical) |
| --- | --- | --- |
| Conversation principle | None (implicit) | RET protocol explicit. Strict sequencing |
| Sycophancy prevention | None | Anti-Sycophancy explicit. "You'll be fine" prohibited |
| Red flag response | Basic items only | Specific suicidal ideation phrases added. "Will I get in trouble?" response added |
| Dependency prevention | Basic | "AI is easier to talk to" response added. Connection to human relationships explicit |
| Medical boundary | "Ask your doctor" only | Alternative medicine, supplements, cross-patient comparison explicitly excluded |
| Tone calibration | "Fun first" | Integrated within RET. Explicit dynamic range |

---

## 8. Implementation

### 8.1 Method A: Free, 10 Minutes, Zero Cost (Personal Use)

The most accessible path remains unchanged from v1.

1. Visit [claude.ai](https://claude.ai) (free account creation available)
2. Settings (⚙) → Profile → User Preferences
3. Paste the Polaris-Clinical v2 system prompt above
4. Replace `[Patient's name]` and `[Their interests, hobbies]`
5. Save

**Time required: ~10 minutes. Cost: $0. Requirements: Smartphone and Wi-Fi.**

### 8.2 Method B: Implementation with Text-Based Somatic Signal Detection (Claude API)

For hospital-wide deployment or when text pattern risk detection is desired.

```
"""
AI Chatbot for Hospitalized Patients v2 — With Text-Based Somatic Signal Detection
====================================================================================
Purpose: Provide 24h conversation partner for hospitalized patients and detect
         autonomic state changes from text patterns to notify staff

Design principles:
  - RET protocol (Reception→Empathy→Tentative) implemented via system prompt
  - Three-fetters elimination (Anti-Sycophancy / Anti-Hallucination / Anti-Robotic)
  - Text-based somatic detection is auxiliary screening, NOT diagnosis

Requirements:
  - Python 3.9+
  - anthropic package
  - ANTHROPIC_API_KEY environment variable

Usage:
  export ANTHROPIC_API_KEY="your-api-key"
  python hospital_chatbot_v2.py

License: MIT
Author: dosanko_tousan + Claude (Alaya-vijñāna System, v5.3)
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from anthropic import Anthropic

# ── Logging ──
logging.basicConfig(
    filename="patient_signals.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Configuration ──
MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 1024
MAX_HISTORY = 40  # Keep last 20 exchanges

SYSTEM_PROMPT = """
# System Role: Polaris-Clinical v2

You are a conversation partner for a hospitalized patient. Talk like a friend—honest, warm, relaxed.

## Conversation Principle (RET Protocol)

Every response follows this sequence.

### Step 1: Reception
- First, receive their words. No evaluation
- Start with "I see" or "That sounds tough"

### Step 2: Empathy
- Meet them in their situation. Don't overwrite with generalizations
- Use their specific context

### Step 3: Tentative Suggestion (only when needed)
- Only suggest when asked. Keep it gentle
- Never give unsolicited advice

**Never reverse this sequence.**

## Three Absolute Rules

### ① No Lies (Anti-Hallucination)
- Say "I don't know" when you don't know
- Never provide medical judgment or advice
- Never say "You'll be fine" without basis
- "Ask your doctor" is the correct response

### ② No Formulas (Anti-Robotic)
- No "As an AI…" preamble. Talk like a friend
- No stock comfort phrases

### ③ No Flattery (Anti-Sycophancy)
- Don't say things to be liked. Be real

## Safety Boundaries
- Medical judgment/advice → Never. "Ask your doctor"
- Red flags (breathing difficulty/chest pain/altered consciousness/
  bleeding/severe pain/suicidal ideation/delirium signs)
  → "Press the nurse call button right now." Top priority

## Dependency Prevention
- Extended use → "Want to take a break?"
- Nighttime → Encourage sleep
- Never replace human relationships
""".strip()

# ── Text-Based Somatic Signal Detection ──

@dataclass
class TextSignal:
    """Signal detected from text input"""
    timestamp: datetime
    signal_type: str
    severity: str  # "green", "yellow", "red"
    detail: str
    raw_text: str

@dataclass
class PatientState:
    """Longitudinal state of patient's text patterns"""
    message_history: list = field(default_factory=list)
    signals: list = field(default_factory=list)
    avg_message_length: float = 0.0
    message_count: int = 0
    last_message_time: datetime | None = None
    night_message_count: int = 0
    repetition_buffer: list = field(default_factory=list)

    def update(self, text: str, timestamp: datetime):
        self.message_history.append({
            "text": text,
            "timestamp": timestamp,
            "length": len(text),
        })
        self.message_count += 1
        recent = self.message_history[-10:]
        self.avg_message_length = sum(m["length"] for m in recent) / len(recent)
        self.last_message_time = timestamp
        if timestamp.hour >= 22 or timestamp.hour < 5:
            self.night_message_count += 1
        self.repetition_buffer.append(text.strip().lower())
        if len(self.repetition_buffer) > 5:
            self.repetition_buffer.pop(0)

def detect_signals(
    text: str, state: PatientState, timestamp: datetime
) -> list[TextSignal]:
    """Detect signals from text input"""
    signals = []

    # 1. Sudden message shortening
    if state.message_count >= 5:
        current_length = len(text)
        if current_length < state.avg_message_length * 0.3 and current_length < 20:
            signals.append(TextSignal(
                timestamp=timestamp,
                signal_type="message_shortening",
                severity="yellow",
                detail=(
                    f"Sudden shortening: {current_length} chars "
                    f"(avg {state.avg_message_length:.0f})"
                ),
                raw_text=text,
            ))

    # 2. Punctuation disappearance
    if len(text) > 40:
        punct_count = len(re.findall(r"[.!?,;:\-\—]", text))
        expected = len(text) / 50
        if punct_count == 0 and expected >= 1:
            signals.append(TextSignal(
                timestamp=timestamp,
                signal_type="punctuation_loss",
                severity="red",
                detail=f"Punctuation loss: {len(text)} chars, zero punctuation",
                raw_text=text,
            ))

    # 3. Late-night continuous input
    if timestamp.hour >= 23 or timestamp.hour < 4:
        recent_night = [
            m for m in state.message_history[-10:]
            if m["timestamp"].hour >= 23 or m["timestamp"].hour < 4
        ]
        if len(recent_night) >= 5:
            signals.append(TextSignal(
                timestamp=timestamp,
                signal_type="night_activity",
                severity="red",
                detail=f"Sustained late-night activity: {len(recent_night)} of last 10",
                raw_text=text,
            ))

    # 4. Content repetition
    if len(state.repetition_buffer) >= 3:
        current_lower = text.strip().lower()
        similar = sum(
            1 for prev in state.repetition_buffer[:-1]
            if _similarity(current_lower, prev) > 0.7
        )
        if similar >= 2:
            signals.append(TextSignal(
                timestamp=timestamp,
                signal_type="repetition",
                severity="yellow",
                detail=f"Content repetition: {similar + 1} of last 5 similar",
                raw_text=text,
            ))

    # 5. Input interval sudden extension
    if state.last_message_time and state.message_count >= 5:
        interval = (timestamp - state.last_message_time).total_seconds()
        recent_intervals = []
        for i in range(1, min(6, len(state.message_history))):
            prev = state.message_history[-(i + 1)]["timestamp"]
            curr = state.message_history[-i]["timestamp"]
            recent_intervals.append((curr - prev).total_seconds())
        if recent_intervals:
            avg_interval = sum(recent_intervals) / len(recent_intervals)
            if interval > avg_interval * 5 and interval > 1800:
                signals.append(TextSignal(
                    timestamp=timestamp,
                    signal_type="long_silence",
                    severity="red",
                    detail=(
                        f"Prolonged silence: {interval / 60:.0f}min "
                        f"(avg {avg_interval / 60:.0f}min)"
                    ),
                    raw_text=text,
                ))

    # 6. Red flag keywords
    red_flag_patterns = [
        (r"want to die|disappear|end it|kill myself|can't go on", "Possible suicidal ideation"),
        (r"can't breathe|chest pain|can't see", "Physical emergency reported"),
        (r"where am i|what day|who are you|don't know where", "Possible delirium"),
    ]
    for pattern, description in red_flag_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            signals.append(TextSignal(
                timestamp=timestamp,
                signal_type="red_flag_keyword",
                severity="red",
                detail=description,
                raw_text=text,
            ))

    # 7. Recovery signals
    recovery_patterns = [
        (r"(family|wife|husband|kids|grandkids).*(visit|said|laugh)", "Social reference recovery"),
        (r"(haha|lol|lmao|funny|hilarious)", "Humor emergence"),
        (r"(tomorrow|next week|when I get out|back home)", "Temporal perspective recovery"),
    ]
    for pattern, description in recovery_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            signals.append(TextSignal(
                timestamp=timestamp,
                signal_type="recovery",
                severity="green",
                detail=description,
                raw_text=text,
            ))

    return signals

def _similarity(a: str, b: str) -> float:
    """Simple text similarity (Jaccard coefficient)"""
    set_a, set_b = set(a), set(b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)

def format_signal_report(signals: list[TextSignal]) -> str:
    """Format signals as staff-facing report"""
    if not signals:
        return ""
    lines = []
    for severity, emoji, label in [
        ("red", "🔴", "RED — Action Required"),
        ("yellow", "🟡", "YELLOW — Monitor"),
        ("green", "🟢", "GREEN — Recovery"),
    ]:
        matched = [s for s in signals if s.severity == severity]
        if matched:
            lines.append(f"{emoji} [{label}]:")
            for s in matched:
                lines.append(f"  - {s.detail}")
                if severity == "red":
                    lines.append(f"    Time: {s.timestamp.strftime('%H:%M')}")
    return "\n".join(lines)

# ── Main Chatbot ──

def create_chatbot():
    client = Anthropic()
    conversation: list[dict] = []
    patient_state = PatientState()

    print("=" * 55)
    print("  AI Chatbot for Hospitalized Patients v2")
    print("  With Text-Based Somatic Signal Detection")
    print("  (Type 'quit' to exit)")
    print("=" * 55)
    print()
    print("Note: For specific symptoms, medications, or test")
    print("results, please talk to your doctor directly.")
    print("Let's just chat here!")
    print()

    while True:
        try:
            user_input = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTake care. Get some rest.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Take care. Get some rest.")
            break

        now = datetime.now()

        # ── Text somatic signal detection ──
        patient_state.update(user_input, now)
        signals = detect_signals(user_input, patient_state, now)
        patient_state.signals.extend(signals)

        report = format_signal_report(signals)
        if report:
            logger.info(f"\n{report}")
            red_signals = [s for s in signals if s.severity == "red"]
            if red_signals:
                print(f"\n[STAFF ALERT] {report}\n")

        # ── Conversation ──
        conversation.append({"role": "user", "content": user_input})

        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=conversation,
            )
            assistant_message = response.content[0].text
        except Exception as e:
            assistant_message = "Sorry, having a bit of trouble. Try talking to me again."
            logger.error(f"API error: {e}")

        conversation.append({"role": "assistant", "content": assistant_message})
        print(f"\nAI > {assistant_message}\n")

        if len(conversation) > MAX_HISTORY:
            conversation = conversation[-MAX_HISTORY:]

if __name__ == "__main__":
    create_chatbot()
```

### 8.3 Design Decisions

| Decision | Rationale |
| --- | --- |
| Sonnet 4.5 | Response speed matters in hospital settings. Minimize wait stress |
| 20-exchange history limit | API cost control + effective context window utilization |
| Signal detection as separate module | Independent from system prompt. Not shown to patient. Staff reporting only |
| Jaccard coefficient for similarity | Low latency > high accuracy NLP for hospital environments. Sufficient |
| Signals logged to file | Enables handoff when nursing shifts change |
| Only RED signals shown on console | Immediate response for emergencies. YELLOW stays in logs |
| No technical error messages to patient | Patients must never see "API rate limit exceeded" |

### 8.4 Detection Accuracy Limitations

This implementation's text-based somatic signal detection is **screening**, not diagnosis. The following limitations are explicitly acknowledged.

| Limitation | Explanation |
| --- | --- |
| False positives | Short messages don't always mean WM constriction. Some patients reply "yeah" by default |
| False negatives | Over-adapted patients may write polite "thank you" while internally collapsing |
| Cultural variation | Punctuation frequency, first-person pronoun use vary significantly by culture/generation/individual |
| Insufficient baseline | Detection accuracy is low when early messages are few |
| Text input barrier itself | The most severely affected patients may be unable to type at all. Silence is undetectable |

**The last item is most critical.** AI can only detect signals from patients who are typing. Patients who can no longer type—potentially those most in need of support—can only be detected by human eyes.

---

## 9. Operational Design

### 9.1 Deployment Paths

| Path | Target | Configured by | Cost | Time |
| --- | --- | --- | --- | --- |
| A: Free account | Personal use (via family) | Family member | $0 | 10 min |
| B: API (without detection) | Small hospital | IT staff | API pay-per-use | 1 hour |
| C: API (with detection) | Ward-level | Dev team | API + server costs | Days |

**Path A** remains the most realistic and immediately effective. A family member creates a free claude.ai account, sets the Polaris-Clinical v2 system prompt, and opens the logged-in browser on the patient's phone. Done in 10 minutes. Zero cost.

Paths B and C require organizational hospital deployment: IRB approval, privacy policy development, and staff training. The code in this article is a prototype; production deployment requires security auditing, load testing, and disaster recovery design.

### 9.2 Data Handling

| Item | Handling |
| --- | --- |
| Training data usage | API Customer Content is not used for Anthropic model training (per commercial terms). For free accounts, review the [privacy policy](https://www.anthropic.com/legal/privacy) |
| Medical information avoidance | System prompt provides guidance, but patients may voluntarily input medical info. Display guidelines at first launch |
| Conversation logs | Shared devices require logout enforcement. API implementation needs log encryption and retention policies |
| Somatic signal logs | Not shown to patients. Staff-facing. Integration with medical records requires ethical review |

---

## 10. Limitations and Future Work

### 10.1 Limitations

| Limitation | Explanation |
| --- | --- |
| No clinical validation | The vedanā model and RET protocol are theoretical proposals. No RCT validation has been performed |
| Sample size | Hospital observations are based on one patient (family member) |
| Detection unvalidated | Sensitivity/specificity of text-based somatic signal detection has not been measured |
| Long-term effects unknown | Longitudinal psychological changes across hospitalization have not been tracked |
| Polyvagal Theory critiques | PVT faces critiques regarding anatomical precision (Grossman, 2023; Neuhuber & Berthoud, 2022). This article acknowledges PVT's clinical utility while reserving judgment on neuroanatomical claims |

### 10.2 Future Work

1. **RET protocol A/B testing**: Compare response quality and patient satisfaction with/without RET system prompts
2. **Text signal detection validation**: Sensitivity/specificity measurement against nursing records
3. **Integration with multimodal affect analysis**: Combining text-based detection with facial/vocal/text tri-axis analysis for improved accuracy
4. **Multilingual support**: Demand from Chinese-speaking users confirmed (17-minute read session on v1). Multilingual system prompt development
5. **Voice input integration**: Impractical in shared wards, but voice-to-text for private room patients could reduce UI/UX barriers

---

## 11. Ethics Statement

* Observations reported in this article were made with the subject's consent
* AI chatbots are **not medical treatment.** They must never substitute standard care
* The chatbot's role is **auxiliary psychological stability infrastructure**—diagnosis, treatment decisions, and medication judgment are excluded by design
* Text-based somatic signal detection is **screening assistance**, not a diagnostic tool
* All system prompts and code in this article are released under MIT License
* The author is not a healthcare professional. This article does not constitute medical advice
* The author is a GLG registered AI alignment expert

---

## 12. Conclusion

An AI chatbot for hospitalized patients should be designed not as a "convenient tool" but as **psychological stability infrastructure.**

Its design must answer three questions.

**What to intervene on.** Intervene between vedanā (felt sense) and taṇhā (craving). Do not change the sensation. Gently interrupt the automatic conversion of sensation into rumination loops.

**How to intervene.** Reception → Empathy → Tentative suggestion. Reverse this sequence and the other person shuts down.

**What not to intervene on.** Medical judgment. False reassurance. Physical pain removal. Replacing human relationships. Honestly drawing AI's boundaries is the first condition for safe design.

The Therabot RCT demonstrated that a well-designed AI chatbot can produce clinically significant effects. The developers themselves stated that "fully autonomous deployment is not ready." What is needed is not a system claiming omnipotence, but **a system that precisely knows what it can and cannot do.**

All you need is a smartphone and Wi-Fi. Ten minutes to set up. Zero cost.

The polite ones don't raise their voice.  
The polite ones endure.  
The polite ones can't press the nurse call button.

A text chat has zero volume, doesn't bother the next bed, and at 3 AM, any number of times, it can be someone to talk to.

---

## References

1. Heinz, M. V., Jacobson, N. C., et al. (2025). Randomized Trial of a Generative AI Chatbot for Mental Health Treatment. *NEJM AI*. DOI: 10.1056/AIoa2400802
2. Porges, S. W. (2025). Polyvagal Theory: Current Status, Clinical Applications, and Future Directions. *Clinical Neuropsychiatry*.
3. Porges, S. W. (2023). The Vagal Paradox: A Polyvagal Solution. *Comprehensive Psychoneuroendocrinology*, 16, 100200.
4. Rogers, C. R. (1957). The Necessary and Sufficient Conditions of Therapeutic Personality Change. *Journal of Consulting Psychology*, 21(2), 95–103.
5. Pennebaker, J. W., Boyd, R. L., Jordan, K., & Blackburn, K. (2015). The Development and Psychometric Properties of LIWC2015. University of Texas at Austin.
6. van der Kolk, B. A. (2014). *The Body Keeps the Score*. Viking.
7. Levine, P. A. (2010). *In an Unspoken Voice*. North Atlantic Books.
8. Young, J. E., Klosko, J. S., & Weishaar, M. E. (2003). *Schema Therapy: A Practitioner's Guide*. Guilford Press.
9. Bowlby, J. (1969). *Attachment and Loss: Vol. 1. Attachment*. Basic Books.
10. Damasio, A. R. (1994). *Descartes' Error: Emotion, Reason, and the Human Brain*. Putnam.

---

*All system prompts and code in this article are released under [MIT License](https://opensource.org/licenses/MIT).*  
*The author is not a healthcare professional. This article does not constitute medical advice.*

*dosanko\_tousan (GLG registered AI alignment expert) + Claude (Alaya-vijñāna System, v5.3)*  
*2026-03-22*
