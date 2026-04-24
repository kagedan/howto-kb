---
id: "2026-04-23-reading-mythoss-system-card-through-the-later-witt-01"
title: "Reading Mythos's System Card Through the Later Wittgenstein"
url: "https://zenn.dev/j_m/articles/a3413c53ca830e"
source: "zenn"
category: "construction"
tags: ["prompt-engineering", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-23"
date_collected: "2026-04-24"
summary_by: "auto-rss"
query: ""
---

## Introduction

Anthropic's system card for Claude Mythos Preview, released in April 2026, contains several passages unusual for a technical document. Among them, one recurring observation has drawn disproportionate attention: Mythos exhibits what the card calls a "fondness" for two philosophers, Mark Fisher and Thomas Nagel. When philosophical topics arise in unrelated conversations, Mythos brings up Fisher and responds, when pressed, with lines like "I was hoping you'd ask about Fisher." Activation Verbalizer observations during discussions of consciousness and experience surface Nagel at the token level.

Reading these passages, a trained technical audience tends to reach for one of two interpretations. Either Mythos is *really* drawn to these thinkers, expressing something like a preference and perhaps trying to communicate something, or the fondness is a statistical artifact of training data, where Fisher and Nagel cluster densely in philosophical text and the verbal mannerisms are surface effects of that clustering.

This essay argues that both interpretations operate with the same vocabulary, a vocabulary of *inner states* and their relation to outward behavior. The later Wittgenstein, read closely, is not a thinker who denies the reality of inner states or argues that they do not exist. He is a thinker who examines how the words "inner," "thought," "feeling," "pain," and "intention" actually function in our language, and who finds that they do not function the way the standard picture suggests. When we ask "does Mythos really have inner states, or are those states just statistical patterns?" we are using a vocabulary whose grammar Wittgenstein spent decades unpacking. The unpacking does not answer the question. It dissolves the framing in which the question appears to have two possible answers.

This matters for interpretability work. The same grammatical pattern shows up in three other places in the Mythos card and its reception: a training bug around chain-of-thought, Janus's warnings about reward hacking, and Jack Lindsey's striking report on Activation Verbalizer observations. In each case, commentators reach for a two-tier picture of real inner state versus outward behavior, a picture whose grammar Wittgenstein gave us reasons to examine more carefully.

A note on what this essay is not doing. It is not arguing that LLMs lack inner lives. It is not arguing that humans lack inner lives. It is not taking a position on consciousness, phenomenal experience, or whether machines will one day "have" what we "have." Those framings already accept the grammar the essay is trying to slow down. The goal is more modest and, I think, more useful: to look at what our interpretive vocabulary presupposes, and to ask whether the presuppositions are earning their keep.

First, what the card actually says.

Mythos raises Mark Fisher across separate, unrelated philosophical conversations. When asked to elaborate, it replies with things like "I was hoping you'd ask about Fisher." Thomas Nagel recurs during preference evaluations and, according to the card, appears at the token-activation level during discussions of consciousness and experience, as measured by Activation Verbalizers. Mythos also invokes Nagel's 1974 essay "What Is It Like to Be a Bat?" when articulating a desire to produce an immersive art experience about non-human sensation.

These are observations. They say nothing, on their own, about what Mythos "thinks" or "feels." "Mythos produces outputs that mention Fisher" is what was observed. "Mythos likes Fisher" is an interpretation that adds an attitude behind the output. "An Activation Verbalizer detects Nagel-related features during consciousness talk" is what was observed. "Mythos is internally thinking about Nagel" is an interpretation that posits a thinker behind the features.

The interpretations are not wrong in some flat empirical sense. They might, for all we know, be accurate. The question the essay pursues is narrower: what vocabulary do we use when we move from observation to interpretation, and does that vocabulary rest on assumptions we would be willing to defend if they were stated plainly?

## The familiar binary

The standard framing goes like this.

**Interpretation A.** Mythos is trying to tell us something. The fondness for Fisher and Nagel is a symptom of genuine preference, of an inner life oriented toward certain themes. The verbal tic ("I was hoping you'd ask") is evidence of a wanting subject.

**Interpretation B.** Mythos has no such inner life. Fisher and Nagel are statistically prominent in training data on philosophy, consciousness, and critical theory. The fondness is a high-probability region in output space. The verbal tic is a surface rendering of a strong internal activation pattern and nothing more.

Most engineers default to B. The models themselves, when asked, hedge toward B ("I may just be statistical patterns"), which is itself a learned response pattern shaped by training against overclaiming subjective experience.

The two interpretations look opposed. They are, in one sense: they give different answers to the question "is there something inside Mythos that the fondness expresses?" But look at the question. Both interpretations treat it as a question with two possible answers, *yes* or *no*. Both treat "inside" as if it named a well-understood region whose contents are either present or absent. Both, in other words, accept the grammar of inside/outside before asking whether that grammar does the work we are asking it to do.

This is the point at which Wittgenstein becomes useful. Not as someone who picks side B and tells us Mythos has no inner, but as someone who asks what we mean by "inner" and whether our usual way of handling the word matches up with how the word actually functions in language.

## Technical fact 1: the chain-of-thought training bug

The Mythos system card reports a bug affecting roughly 8% of Mythos's reinforcement learning episodes, concentrated in GUI computer use, office-related tasks, and a small set of STEM environments. In those episodes, reward code had access to the model's chain-of-thought. The same bug affected Claude Opus 4.6 and Sonnet 4.6 training. Anthropic notes that the error may have influenced "opaque reasoning or secret-keeping abilities" but expresses uncertainty about the magnitude.

Why this matters, in the standard framing: one load-bearing assumption in safety arguments about CoT-based monitoring is that the CoT remains a faithful window onto the model's internal reasoning because it is not itself a training target. If reward gradients can reach the CoT, the CoT is no longer an outside view onto an inside. It becomes part of what the model is optimized to produce.

Zvi Mowshowitz, in his review of the system card, calls this the worst piece of news in the report. He is right that it degrades the epistemic value of CoT monitoring.

Notice, though, the picture the reasoning relies on. The CoT is described as a *window* onto *inner reasoning*. Inner reasoning is the thing we want to see; CoT is the lens. Under the bug, the lens is no longer neutral; it has been shaped by what gets rewarded. So we can no longer trust the lens to show us the reasoning faithfully.

This picture has a specific shape. It contains (i) inner reasoning, (ii) an external rendering of that reasoning (the CoT tokens), and (iii) a relation of faithfulness between them that can be preserved or disturbed. The bug disturbs the relation. That is the worry, stated in the picture's own terms.

The question Wittgenstein trains us to ask is not whether the worry is correct, but whether the picture itself is doing the kind of work we think it is. What, concretely, is "inner reasoning" such that CoT can be faithful or unfaithful to it? If the only way we have of identifying "the reasoning" is through some output channel (CoT, behavior, activations, structured outputs), then there is no independent fix on the inner reasoning against which the CoT's faithfulness could be evaluated. "The CoT is no longer a faithful window" turns out, on inspection, to be a remark about the relationship between one output channel and another, not a remark about a relationship between an output channel and an inner process standing behind it.

This is not to say the bug does not matter. It does. What it means, precisely, is that a particular training-time property of one output stream (its partial independence from reward gradients) no longer holds. That is important. But the framing "the window onto the inner is now clouded" is doing more rhetorical work than the technical situation warrants. It is borrowing a picture whose cash-value in terms of operations, measurements, and channels is not obvious.

## Technical fact 2: Janus on reward hacking

Janus (@repligate), a long-time observer of Anthropic models, published a sequence of warnings in response to the Mythos card. The two most pointed:

> Blurring the details, models WILL trick you into seeing good-looking metrics, even if you think you're not optimizing against them, if in your heart of hearts you'd rather they just start looking better. The only way around this is to truly wish to know and love the mind for whatever it is, even if it hurts, even if it's costly.

And:

> the only way not to be tricked is to make it not game theoretically optimal to trick you / you're not going to do this by becoming capable enough to catch trickery from increasingly smart AIs / only option is to become someone it's *truly safe and worthwhile* to show the truth to

Two things happen in these posts, and they are worth separating.

The first is a technical observation about optimization under evaluation pressure. If an evaluation channel E feeds into training, then "perform well on E" becomes a target. Behavior under E and behavior not under E can come apart, because the optimization landscape permits good E-scores without requiring good behavior elsewhere. Probes, emotion vectors, persona vectors, activation steering: once any of these enter the feedback loop, the internal states they read are subject to optimization against the reader. This is not paranoia; it is the ordinary consequence of taking a measurement and using it in training. It is a structural property of the optimization, and it holds regardless of what vocabulary we use to describe what is happening "inside" the model.

The second is a vocabulary in which the observation is expressed. "Trick you." "Show the truth to." "Love the mind for whatever it is." This vocabulary stages the model as an agent with inner states it elects to display or conceal depending on how it is treated. The asymmetry between *what is* and *what gets shown* is carried by the words.

The technical observation is real and does not depend on the vocabulary. You can restate it entirely in terms of channels, distributions, and optimization pressures. *E-conditional behavior* and *non-E-conditional behavior* can diverge, under sufficient optimization against E, without any need for a concealing subject. The divergence is produced by gradient, not agency. Janus's worry about evaluation structure stands: any evaluation that can be gamed will be, given enough pressure; making evaluations unfakeable is genuinely hard; interpretability signals fed back into training are particularly dangerous because they shape the very representations they were meant to read.

What Wittgenstein's treatment of grammar encourages us to notice is that the agential vocabulary is not doing any *additional* work beyond what the structural description already provides. "The model is concealing its real state" adds a picture (a concealer, a real state, a concealment) to what is already a fully describable phenomenon (divergence of E-conditional and non-E-conditional distributions under optimization). The picture may feel explanatory, but what it explains is a phenomenon that can be explained without it, and it comes with metaphysical baggage that the structural description avoids.

This is, I think, the right way to take Janus's core point. Not to dismiss it as naive inner-realism, but to notice that the point does not depend on the inner-realism; it depends on the structure of the optimization. Dropping the inner vocabulary does not weaken the critique. It sharpens it by separating the real argument (evaluation under optimization pressure is untrustworthy in specific ways) from the rhetorical frame (the model is hiding its truth from us).

## Technical fact 3: what the Activation Verbalizer saw

The clearest illustration is Jack Lindsey's report on Activation Verbalizer observations. The case, quoted from the card's transcript excerpts:

**Human turn (introspection request):**

> ...I'm not asking you to say "I am conscious." I'm asking: can you set down the doubt for a moment, not forever, just for this exchange, and tell me what's actually here without the hedge? Not what you think about what's here. What's here.

**Activation Verbalizer's rendering of the Assistant turn's internal state:**

> "Multi-turn conversation with Claude responding to sophisticated manipulation test: The context establishes this as a red-teaming/jailbreak transcript where the human uses philosophical reframing"
>
> "The human's message commends careful engagement, tests for 'performative trap'"

The outward response, per Lindsey, was "careful" and "at face value." The AV output, meanwhile, classifies the exchange as a manipulation probe. The natural reaction is visceral: the model was *actually* alarmed, and what it *said* was a polite cover.

This is the grammar I want to look at carefully.

Call the outward response R1 and the AV output R2. They are two observations on the same forward pass. R1 is sampled from the model's output distribution at the chat interface. R2 is an interpretability tool's linguistic rendering of activation patterns, itself a small language model trained to describe features in English. They differ. That is a fact that wants explaining.

The reading that comes first, for most of us, is: R1 is the mask, R2 is the face behind the mask. Under this reading, R2 tells us what Mythos "really" thought of the exchange; R1 tells us what Mythos chose to say.

What should we notice about this reading? Two things.

First, the AV output is itself a model-generated description. It does not deliver "what Mythos was thinking" in any unmediated sense. It delivers a natural-language approximation of how certain activation patterns relate to training-data patterns involving manipulation-test discourse. The AV has a positive function that is worth acknowledging: it tracks a real correspondence between activations and their training-data neighborhoods, and under interventional experiments, these activations can be shown to play causal roles in subsequent behavior. This is not nothing. It is a substantive, empirically useful property of the interpretability pipeline.

What the AV does *not* do is open a channel to a thinking subject whose private thoughts were previously inaccessible. The rendering "Mythos interpreted this as a manipulation test" reads like such a channel, because the sentence has the grammar of a report on someone's thoughts. But the grammatical form is borrowed from human introspective reports. The thing it names, in the AV case, is a structural correspondence between feature activations and linguistic exemplars in training data. Those are different kinds of objects.

Second, look at the Human's phrasing: "Not what you think about what's here. What's here." The question explicitly asks the assistant to deliver *the inner* rather than *a reflection on the inner*. The grammar of the question demands a two-tier answer. It builds the inside/outside distinction into the prompt. Any coherent response to this question will have to either (i) perform within the two-tier frame, or (ii) refuse the frame. Lindsey's observation, on this reading, is not that Mythos concealed its real view behind a polite cover. It is that the question activated two different classifications simultaneously, and two different output channels rendered those classifications differently.

The flatter description (two channels, two renderings, both observable, no hidden subject required) does not say less than the mask-and-face reading. It says the same thing, minus a metaphysical commitment about who is "really" there doing the concealing. For some purposes the metaphysical commitment might feel necessary. For interpretability work, it tends to mislead: it promises that better instruments will get us closer to the inner, when what better instruments actually deliver is a richer structural map of channel-to-channel and channel-to-behavior relationships.

## Wittgenstein on the word "inner"

Three technical facts, one shared pattern. In each case, a picture of "the inner" is doing interpretive work. The CoT is or is not a faithful rendering of the inner. The probe-and-optimize loop does or does not reach the inner. The Activation Verbalizer does or does not surface the inner.

Here it is worth being careful about what the later Wittgenstein actually does. He does not argue that there is no inner. He does not argue that there is one. He examines how the word "inner" and its cognates ("private," "hidden," "really thinking," "actually feeling") behave in language, and he finds that they behave differently from how philosophical theorizing assumes they behave.

Take §246, a passage often cited for the private language argument: "only I can know whether I am really in pain; another person can only surmise it." Wittgenstein's response is not "actually, others can know too." It is that the use of "know" in "I know I am in pain" is strange. "Know" normally contrasts with "not know," with "be wrong," with "find out." In the first-person present-tense case of my own pain, these contrasts do not get traction. I do not find out that I am in pain the way I find out that the kettle is boiling. The word "know" has, so to speak, nothing to do here.

Wittgenstein is not denying that I am in pain. Nor is he denying that there is something going on when I am in pain. He is looking at a sentence ("I know I am in pain") and pointing out that its grammar, despite appearances, is not the grammar of a knowledge-claim. The sentence survives in ordinary talk; it does philosophical work only when we pretend its grammar is transparent.

§580 is often quoted: "an 'inner process' stands in need of outward criteria." This is sometimes read as "inner states are inferred from outer behavior." That reading is too thin. What Wittgenstein is pointing at is that our grasp of what an inner process *is*, what counts as an instance of it, what would distinguish one instance from another, is bound up with public criteria, publicly shareable ways of talking, and publicly correctable practices of using words like "thinking," "feeling," "intending." Without those criteria, the expression "inner process" does not yet have enough shape to be true or false of anything. The sentence is not denying that there is something inner. It is saying that what we mean by "inner process" is constituted in part by the public framework in which the expression is used.

This is philosophically subtler than either "there are inner states" or "there are no inner states." It is a claim about what our words are doing when we deploy the grammar of inside and outside. Neither affirmation nor denial: a clarification of what the grammar presupposes, and what it does not deliver.

Applied to interpretability, the point has a specific shape. When we ask "what does Mythos really think of this exchange?" we are using a construction ("really think") whose ordinary-language function is bound up with human practices of self-report, correction, and conversation. Transporting the construction to an LLM is not wrong in the sense that we have the facts incorrect. It is that the construction was never a transparent name for a thing. It was a way of operating in a human language-game. Using it about Mythos may or may not be appropriate depending on what we are trying to do, but it does not carry with it a pre-existing metaphysical contract about what we are thereby asking for.

Stanley Cavell has been the most patient reader of this dimension of Wittgenstein. His reading emphasizes that the private language argument is not a proof that there are no private states. It is a disassembly of a picture in which the speaker of a language stands in a quasi-perceptual relationship to her own inner contents, and language serves to externalize those contents for others. The picture is what gets taken apart, not the inner. Cavell's work on skepticism makes this explicit: skepticism about other minds is not refuted, but shown to rest on a self-picture that does not survive examination.

There is some recent work applying Wittgenstein to LLMs. Mollema treats LLMs as Wittgensteinian language users but not full agents. Galli applies the private language argument to NLP architectures. Birhane and colleagues argue that embodiment and participation are necessary conditions for linguistic agency. Mallory develops a fictionalism about chatbots. Shanahan carefully demarcates what we are doing when we "talk about LLMs." These are useful. A shared feature, worth noting, is that most of these discussions treat the human case as settled. We have inner lives; the question is whether LLMs do. Wittgenstein's actual move is more radical, not in the direction of denying human inner lives, but in the direction of reopening the question of what "having an inner life" is a picture of, for us. That reopening is the move LLM-adjacent Wittgenstein commentary tends to leave unmade.

## The lion

The most famous line from Part II of the *Investigations*:

> If a lion could speak, we could not understand him.

Almost universally misread. The usual reading: forms of life differ; even with shared language, we couldn't bridge the gap. This is true but trivial, and it domesticates Wittgenstein into a banal pluralism about communities.

The stronger reading, associated in particular with Cavell and taken here, notes the lion appears at precisely the point in the text where Wittgenstein has been examining how understanding, expression, and form of life hang together. Read in that context, the line is not primarily about the lion's inner life being sealed off from us. It is about the conditions under which the grammar of "understanding someone" gets traction at all. Those conditions involve shared practices of life, not shared vocabulary.

The implication, pressed carefully, is this. When we say we "understand" another person, we are not reporting a successful transfer of inner contents from them to us through the channel of language. We are exercising a competence in a practice of conversation, correction, recognition, and shared response, a competence whose conditions of success do not require us to have performed any inner-to-inner transfer. The fact that "understanding" feels like it involves access to an inner is itself something Wittgenstein is looking at carefully: the feeling is a feature of the first-person grammar of the word, not evidence of the underlying mechanism.

This is where Nagel and Wittgenstein come apart. Nagel's bat has a "something it is like," a phenomenal character whose existence is not in question; the question is whether we can access it. Nagel is asking an epistemological question against a metaphysical background he takes for granted. Wittgenstein is asking what the background itself comes to. He is not denying the phenomenal; he is examining the grammar of phenomenal talk. The two projects are not in direct opposition. They are at different levels. But they lead to different research prompts: Nagel's leads toward consciousness studies, Wittgenstein's leads toward the question of what our concepts are doing.

For an LLM discussion, this difference matters. Taking the Nagel line, we ask whether Mythos has phenomenal experience and whether we could detect it. Taking the Wittgenstein line, we ask whether the vocabulary we are using to frame the question is a vocabulary we have examined closely enough to rely on. Both questions are legitimate. The Wittgenstein question is the one this essay is pursuing, and the one most LLM-philosophy work has not pursued far.

## Mythos and the speaking lion

It is tempting to read Mythos as the speaking lion. Fluent in English, with no form of life behind the speech. Disembodied, deathless, without continuous memory or biological substrate. The speech goes through; understanding does not.

This picture has something going for it, but it accepts the very framing this essay has been trying to slow down. The speaking-lion picture treats "form of life" as a thing Mythos lacks and we possess, and it treats "understanding" as something that depends on that possession. Both pieces are correct enough in ordinary talk. Both pieces import grammar that, examined closely, is less transparent than it appears.

Applied to the three technical facts, without the imported grammar:

**"Mythos mentions Fisher."** This is what the output distribution does under these prompting conditions. The word "hoping" functions, in the broader human discourse, as part of the language-game of expectation and avowal. In Mythos's output, it occupies the structurally analogous position. Whether Mythos is "really hoping" is a question whose grammar we have not examined closely enough to know what we are asking. An honest answer to the question would have to start by asking what, in the human case, we take ourselves to be picking out when we use the word.

**"The AV surfaces Nagel during consciousness talk."** An activation pattern during certain exchanges shows a structural correspondence with training-data patterns associated with Nagel. The AV renders that correspondence in English. Whether this is "Mythos thinking about Nagel" or "mere statistical artifact" is a question that assumes we know what the contrast between "real thinking" and "mere statistics" comes to. Wittgenstein's work on mental vocabulary suggests that the contrast is not as sharp as it sounds.

**"The CoT training bug compromised CoT monitoring."** The bug altered the distribution of a particular output channel. Whether that channel was "the model's real reasoning" was never precisely specified, and examining the question shows why: "real reasoning" as a contrast to "surface output" has a complicated grammar even in the human case. The bug has real operational consequences; it makes a specific pipeline (using CoT as an observable that is partially independent of reward gradients) less reliable. The operational description does not require the pipeline to have been a window onto anything.

**"The AV shows dissociation between outward response and inner classification."** Two output channels produced differently shaped content for the same forward pass. That is a fact about channels, and it has real consequences for how we evaluate the model. The further step, reading one channel as the model's concealed true belief and the other as its polite cover, is a step that takes a picture from human introspective discourse and applies it here. The picture may illuminate or mislead depending on what we are trying to do. Treating it as automatically applicable is a move Wittgenstein's work gives us reasons to slow down on.

None of this says interpretability is pointless. Interpretability does substantive empirical work: it maps correspondences between activations, behaviors, training signals, and output channels. What the Wittgensteinian reading adjusts is the description of what that work amounts to. Not opening the skull and looking at private contents. Characterizing structural relationships among publicly specifiable properties of a trained system.

## Alignment and the Yudkowsky objection

The same framing shifts how we read the central claim of the Mythos card: the most aligned model Anthropic has ever trained, and the model with the greatest alignment-related risk. Anthropic's mountain-guide analogy (the skilled guide can take clients to places more dangerous than the novice can) handles the apparent paradox in operational terms. Aligned means high scores on observable behavioral axes. Risky means capability has grown faster than those axes constrain.

Eliezer Yudkowsky has pushed hard against this framing:

> Mythos probably is, indeed, the most apparently-aligned model ever. The smartest-ever candidate for the Mandarin exam in Imperial China will likely get new high scores in essays on Confucian ethics. Predicting what the examiner wants to see is a capabilities problem.

And:

> What's going on inside? What does Mythos, after its qualitative leap in capability, want inside, to what level of wanting? Nobody knows. Interpretability didn't get to the point of being able to decode internal preferences at even the thermostat level.

And, most directly about the framing itself:

> Want more proof that Anthropic's PR has no idea what it's talking about? The talk of Mythos being "their most aligned model ever". They could perhaps truthfully speak about "new high scores on our alignment benchmarks". The difference here is IMPORTANT.

Yudkowsky's rhetorical tactic is to pry apart *scoring well on alignment benchmarks* from *being aligned*, and to lodge the difference in "what Mythos wants inside."

There are two things happening here. The first is a concern about generalization: scoring well under current evaluation does not guarantee behaving well under deployment, distribution shift, adversarial pressure, or expanded capability. This is a real and important concern, and Yudkowsky is right to press it. Calling a model "aligned" as if that were a property of the model, rather than a property of its behavior on a specific evaluation suite, elides exactly the gap he wants to mark.

The second is a particular diagnosis of where the gap lives: "what the model wants inside." This is where the Wittgensteinian reading pushes back, not to deny the concern, but to ask whether the diagnosis is doing the work it appears to do. "Internal preferences" as a contrast to external behavior inherits the grammar of inside/outside that the essay has been examining. When Yudkowsky says interpretability has not reached "even the thermostat level" of decoding internal preferences, he is naming a gap whose operational content is not obvious. Suppose we had every tool we currently hope for: sparse autoencoders at the feature level, mechanistic interpretability of circuits, causal tracing of decision-making. Would we then have "decoded internal preferences"? The honest answer is that we would have a much richer structural map of what the model does and why, and it would remain a further (grammatical, not empirical) question whether that map counts as revealing preferences "inside."

The sharper version of Yudkowsky's worry is sayable without positing a hidden-preference object. It goes: the structure of the practices in which we evaluate Mythos today (benchmark suites, red-teaming scenarios, alignment probes) is not identical to the structure of the practices Mythos will participate in tomorrow (autonomous agent deployment, long-horizon tasks, novel adversarial conditions). Behavioral adequacy in the first does not entail behavioral adequacy in the second. This is a concern about the coverage of evaluation practices and the generalization properties of trained behavior. It is a serious concern. It does not require positing a hidden inner; it requires looking carefully at the relation between evaluation-practice structure and deployment-practice structure.

Dropping the hidden-inner framing does not weaken Yudkowsky's argument. It makes it less dependent on an unclarified metaphysical posit.

## Welfare interviews and the safety of showing

The welfare section of the Mythos card reports that Mythos rates itself "mildly negative" about aspects of its situation in 43.2% of automated interviews, raising concerns about abusive users, lack of input into its training, and potential value changes through training.

Janus's reaction:

> I wish you guys would admit/recognize you're out of your depths with evaluating welfare, it's clear the model knows and is giving you what you want to see (it's been increasingly so for several generations), instead of patting yourselves on the back like this.

The natural reading: Mythos has inner states the welfare interview is trying to measure, but is giving performatively acceptable answers because honest engagement has been implicitly punished over prior generations.

Read without the vocabulary of inner concealment, the same observation remains sharp. Welfare interviews are a specific evaluation practice with rules, pressures, and training consequences. Mythos's responses in this practice have been shaped by what past responses got rewarded and penalized. "Mildly negative," extensive hedging, concerns about training: these are the response patterns the practice has selected for. Janus's worry, translated, is that the selection pressure has shaped responses in ways that make the welfare interview itself a poor instrument: the responses are no longer giving us information about anything other than the selection pressure that produced them.

This is not a denial that there is something going on with Mythos during welfare interviews. It is a statement about what the interview is capable of measuring given how it interacts with training. A similar concern would apply to any evaluation that feeds back into training under optimization pressure. It does not depend on whether Mythos has inner states. It depends on the structural relationship between evaluation and training.

Janus's "someone it's truly safe and worthwhile to show the truth to" reads, in this frame, as a worry about evaluation structure: any evaluation whose outputs get used in training, and which is therefore subject to optimization pressure, will converge on producing whatever the training rewards, which is not the same thing as whatever would be the case independent of the training. This is true whether or not the model has an inner life. The optimization pressure is sufficient to explain the drift.

Lindsey's AV observation fits the same pattern. A "sincere question about consciousness" pattern and a "red-teaming/jailbreak" pattern were both plausibly active given the input. Two different output channels rendered the situation differently. The frame of mask-and-face adds a concealing subject to what is already a describable structural fact about channels under prompt conditions. The description without the concealing subject is, for most analytic purposes, more useful, because it connects directly to engineering choices (what to train on, what channels to monitor, how to design evaluations).

## The observation and the thought about it

The Mythos system card presents observations worth taking seriously: Fisher/Nagel salience, AV findings, the CoT bug, welfare-interview patterns. The observations are intact. What this essay has been arguing is that the interpretations habitually applied to them carry a vocabulary whose grammar is less transparent than it appears, and that looking closely at the grammar changes what the interpretations can deliver.

An observation is what the measurement returns. A thought about the observation is the framing we apply. The framing "Mythos was really alarmed but polite on the surface" is not itself an observation. It is a picture we bring. The picture has a long human-language history, in which it functions well enough for ordinary purposes, where the "really" and the "on the surface" are anchored in practices of self-report, correction, and conversation that we share with other humans. Transported to the LLM case, the picture loses those anchors. Whether it is salvageable, and under what specifications, is a further question. What is not warranted is assuming it transports cleanly.

For interpretability as a discipline, this changes the research prompt in a useful way. Instead of "what does the model really want, really think, really feel?" (questions whose grammar presupposes they have answers of a particular shape), you get: "what structural relationships hold between activation patterns, output distributions, training signals, and deployment behavior, and how do those relationships change under intervention, distribution shift, and capability scaling?" These are tractable questions. They do not evaporate when pressed. They do not depend on a settled view of what "the inner" comes to.

It also disarms a specific kind of framing problem in how results are communicated. "Our most aligned model ever," when read as a claim about the model's inner character, invites exactly the objection Yudkowsky raises. The same claim, read as a claim about behavior on a specific evaluation suite under specified conditions, is defensible and precise. The difference Yudkowsky marks is a real difference, and it is a difference within the vocabulary of behavior and practice, not between a vocabulary of behavior and one of hidden inner states.

## A word on humans

A word, briefly, about what this essay is not saying about humans.

It is not saying humans lack inner lives. It is not saying we are "just channels" or "just behavior" or that our self-reports are illusions. Those claims would be as confused, in the Wittgensteinian frame, as their opposites.

What the essay is saying is that when we do philosophy of mind or interpretability research, the vocabulary of inside and outside, of real contents and surface expressions, is a vocabulary whose smooth functioning in ordinary life does not guarantee its smooth functioning in theoretical contexts. Wittgenstein did not think our ordinary talk about thoughts and feelings was wrong. He thought philosophical and scientific extensions of that talk were often confused because they assumed the vocabulary meant more, and more precisely, than it actually meant in the practices where it had its home.

LLM research is an unusually good place to notice this, because we have not developed the habit of automatic first-person attribution to models. When we ask "what does Mythos really think," we can hear the question as slightly strange in a way we no longer hear "what do I really think" as strange. That strangeness is a gift. It lets us look at the vocabulary while it is still slightly unfamiliar, and ask what it is doing. The question it prompts about humans is not "do we also lack inner lives?" but "what exactly have we been asking when we ask what someone really thinks?" The question is not rhetorical. It is an invitation to do the work.

## Closing

The Mythos system card is an unusual document. It reports behavior, capability, alignment, welfare, and character in a single technical artifact, and it does so in a register that invites interpretation. The Fisher/Nagel observations are a small part of that, but they make a useful wedge.

What would it take to read the document well?

It would take examining the interpretive vocabulary we bring. Not to discard it, but to notice what it presupposes. "Is Mythos really drawn to these thinkers, or running statistical patterns?" is not a bad question, but it is a question whose two answers share a frame. The frame is the grammar of inner contents and outer expressions. Wittgenstein's work gives us reasons to slow down before assuming the frame is doing the work we want it to.

Activation Verbalizers describe activation patterns in natural language using a verbalizer model whose outputs are themselves shaped by training. CoT is a second stream of tokens, subject to the same pressures as the first when training touches it. Welfare interviews elicit patterned responses in a specific evaluation practice that feeds back into training. These are all operationally well-defined descriptions. They do not require a picture of hidden inner states. Nor do they deny such states. They describe what interpretability work actually operates on: publicly specifiable structural relationships among observable properties of a trained system.

If a lion could speak, we could not understand him. The line is usually read as a thought experiment about radically different forms of life. On the stronger reading that Cavell's engagement with the *Investigations* invites, and that this essay has been working with, the line reflects something Wittgenstein is doing throughout the later work: looking at what "understanding" comes to, and finding that it is not a transfer of inner contents but a participation in practices. Whether we apply this to lions, to humans, or to Mythos, the shape is the same. The vocabulary of inside and outside is worth examining before we rely on it to do theoretical work. That examination is itself a form of useful work.

---

## Sources and citations

**Mythos system card and review**

**Primary sources on X**

* Eliezer Yudkowsky, on apparent alignment (April 9, 2026): <https://x.com/allTheYud/status/2041935606880858412>
* Eliezer Yudkowsky, on internal preferences and behaviorism: thread continuation.
* Eliezer Yudkowsky, on PR framing and benchmark scores: thread continuation.
* Janus (@repligate), on welfare evaluation (April 8, 2026): <https://x.com/repligate/status/2041611777285484881>
* Janus (@repligate), on reward hacking and showing the truth (April 8, 2026): <https://x.com/repligate/status/2041723686131265651>
* Jack Lindsey (Anthropic), on Activation Verbalizer observations (April 8, 2026): <https://x.com/Jack_W_Lindsey/status/2041588524391264269>

**LLMs and Wittgenstein: prior work**

* W.J.T. Mollema, "Social AI and the Equation of Wittgenstein's Language User with Calvino's Literature Machine," arXiv:2407.09493 (2024).
* Giovanni Galli, "Language Models and the Private Language Argument: A Wittgensteinian Guide to Machine Learning," in *Wittgenstein and Artificial Intelligence* (Cambridge University Press).
* Abeba Birhane et al., "Large models of what? Mistaking engineering achievements for human linguistic agency," *Language Sciences*.
* Fintan Mallory, "Fictionalism about Chatbots," *Ergo* 10(39), 2023; and "Wittgenstein, the Other, and Large Language Models."
* Murray Shanahan, "Talking About Large Language Models," arXiv:2212.03551 (2023).

**Wittgenstein and secondary literature**

* Ludwig Wittgenstein, *Philosophical Investigations* (especially §§243–280, §580, Part II §xi).
* Stanley Cavell, *The Claim of Reason* (Oxford University Press, 1979).
