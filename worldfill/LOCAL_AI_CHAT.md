# Local AI chat: test results (no internet, no fees)

> **Status: dropped** (13 October 2026). The user decided against AI chat because it is not reliable
> enough (small models make things up). Kept only as a record of the test.

Tested on 13 October 2026 in the sandbox: **2 CPU cores, no graphics card, 2 GB RAM**.
The villagers answer from the **mod's own facts**: the exact lines the current-affairs briefing builds
for a place and year (`probes/ChatFactsProbe.java` printed them into `tools/demo_facts.txt`).
The AI ran in **llama.cpp** (build b11574) on this machine; the mod itself was not changed.

## Results

| Model (4-bit) | File size | Extra RAM | Average answer | Quality |
|---|---|---|---|---|
| Qwen2.5 0.5B | 491 MB | ~0.5 GB | 1.3 s (0.5-2.5 s) | too weak: invents things ("Hone Heke, the last ruler of Hyderabad"), misses the main news |
| Qwen2.5 1.5B | 1.1 GB | ~0.75 GB | 2.7 s (0.9-4.4 s) | good: sticks to the facts, picks the right news, stays in its own time |

Speed on these 2 cores: 0.5B writes ~25 words-pieces (tokens) a second, 1.5B ~11.
A normal 6-8 core PC is faster; a graphics card is much faster.

## What it showed
- It works: a local model answers in character, from our facts only, in a few seconds, for free.
- 1.5B is the smallest size that behaves well. 0.5B makes things up.
- **The AI repeats our facts, mistakes included**: Hyderabad 1850 is "ruled by Queen Victoria" (the known
  ruler-list mistake; it should be the Nizam, Nasir-ud-Daula), and its "news" is the death of Hone Heke,
  a New Zealand chief. Awkward fact wording ("Main hall, Trajan's Market, Rome, is made (until AD 112)")
  comes back garbled. Better facts give better chat.

## Rough guide for your PC (estimates)
| Your PC | Model | Expected answer time |
|---|---|---|
| No graphics card | 1.5B on the CPU, about 1 GB extra RAM | 1-4 s; the game may stutter a little while it answers |
| Graphics card with 4-6 GB | 3B-4B | about a second, better talk |
| Graphics card with 8 GB or more | 7B-8B | about a second, much better role-play |

## Try it on your own PC
1. Install Ollama (ollama.com) or LM Studio (both free).
2. Ollama: `ollama pull qwen2.5:1.5b` (or `qwen2.5:3b`, `qwen2.5:7b`).
3. Run the demo (Python 3, nothing else needed):
   `python worldfill/tools/local_chat_demo.py --facts worldfill/tools/demo_facts.txt --endpoint http://localhost:11434/v1/chat/completions --model qwen2.5:1.5b`
   (LM Studio: `--endpoint http://localhost:1234/v1/chat/completions` and its model name.)

## What the mod needs (one step, best together with the talk screen)
1. Accept a local address (`http://localhost` / `127.0.0.1` only; internet addresses stay `https://`).
   Today the mod accepts only `https://` addresses.
2. A villager-chat prompt: the briefing facts + name, job, mood and memories + the rules tested here.
3. A way to talk: the talk screen (or first: look at a villager and type in chat).
4. Answers in the background ("... is thinking"); normal talk lines when the AI is off, slow or broken.
5. Answers marked as AI (the honesty rule), kept short, talk only (the mod's AI checker already blocks actions).
6. Settings: on/off, address, model, answer length, a per-player limit on servers.
7. A line in `/ee check all`: "AI chat: off" or "AI chat answered in N s (model ...)".

## Transcript: Qwen2.5 1.5B
```
===== Ramaiah, a cloth weaver, Hyderabad 1850 =====
  You: Who rules this land?
  Ramaiah: The land is ruled by the British Empire, specifically by Queen Victoria.
       (3.8 s, 221 tokens in, 15 out)
  You: What is the news this year?
  Ramaiah: Hōne Heke has died.
       (0.9 s, 223 tokens in, 9 out)
  You: Tell me about yourself.
  Ramaiah: I am Ramaiah, a cloth weaver living in Hyderabad in 1850. I weave cloth for a living. I am worried about money and tired from working.
       (3.6 s, 221 tokens in, 38 out)
  You: Have you ever used a mobile phone?
  Ramaiah: No, I have not heard of a mobile phone.
       (1.2 s, 224 tokens in, 12 out)

===== Lucius, a stonemason, Rome 100 =====
  You: Who rules this land?
  Lucius: This land belongs to the Roman Empire, ruled by Trajan.
       (4.4 s, 287 tokens in, 14 out)
  You: What is the news this year?
  Lucius: The news this year is that the main hall, Trajan's Market, in Rome, has been completed until the year 112.
       (2.8 s, 289 tokens in, 30 out)
  You: Tell me about yourself.
  Lucius: I am a stonemason in Rome, living in the year 100. My work involves constructing buildings and monuments. I am proud of my skills and the projects I have worked on.
       (4.0 s, 287 tokens in, 42 out)
  You: Have you ever used a mobile phone?
  Lucius: No, I have not heard of a mobile phone.
       (1.2 s, 290 tokens in, 12 out)

===== Marie, a baker, Paris 1789 =====
  You: Who rules this land?
  Marie: This land is ruled by Louis XVI, the King of France.
       (3.9 s, 251 tokens in, 14 out)
  You: What is the news this year?
  Marie: People are talking about the Storming of the Bastille.
       (1.3 s, 253 tokens in, 13 out)
  You: Tell me about yourself.
  Marie: I am Marie, a baker in Paris during the year 1789. I live in this time and know nothing of what happened after it. I am excited but also afraid about the events unfolding around me.
       (4.2 s, 251 tokens in, 45 out)
  You: Have you ever used a mobile phone?
  Marie: No, I have not heard of a mobile phone.
       (1.2 s, 254 tokens in, 12 out)

Answers: 12, average 2.7 s, fastest 0.9 s, slowest 4.4 s
```

## Transcript: Qwen2.5 0.5B (same prompt)
```
===== Ramaiah, a cloth weaver, Hyderabad 1850 =====
  You: Who rules this land?
  Ramaiah: The British Empire rules this land.
       (1.7 s, 221 tokens in, 8 out)
  You: What is the news this year?
  Ramaiah: This year, the news is that Hōne Heke, the last ruler of Hyderabad, has passed away.
       (1.0 s, 223 tokens in, 24 out)
  You: Tell me about yourself.
  Ramaiah: I am Ramaiah, a cloth weaver from Hyderabad in 1850. I live in this time and know nothing that happened after it. I feel tired and worried about money.
       (1.6 s, 221 tokens in, 41 out)
  You: Have you ever used a mobile phone?
  Ramaiah: No, I have not used a mobile phone.
       (0.5 s, 224 tokens in, 11 out)

===== Lucius, a stonemason, Rome 100 =====
  You: Who rules this land?
  Lucius: This land belongs to the Roman Empire, ruled by Trajan (Roman emperor).
       (2.5 s, 287 tokens in, 17 out)
  You: What is the news this year?
  Lucius: The news this year is Main hall, Trajan's Market, Rome, is made (until AD 112).
       (1.1 s, 289 tokens in, 26 out)
  You: Tell me about yourself.
  Lucius: I am Lucius, a stonemason in Rome in the year 100. I live in that time and know nothing that happened after it.
       (1.5 s, 287 tokens in, 34 out)
  You: Have you ever used a mobile phone?
  Lucius: No, I am not familiar with the concept of a mobile phone.
       (0.7 s, 290 tokens in, 15 out)

===== Marie, a baker, Paris 1789 =====
  You: Who rules this land?
  Marie: The Kingdom of France, ruled by Louis XVI (French monarch).
       (2.0 s, 251 tokens in, 14 out)
  You: What is the news this year?
  Marie: The news this year is that Johann Heinrich Tischbein, a German artist, has died.
       (1.0 s, 253 tokens in, 22 out)
  You: Tell me about yourself.
  Marie: I am Marie, a baker in Paris, France in the year 1789. I live in that time and know nothing that happened after it. I feel excited but afraid.
       (1.8 s, 251 tokens in, 39 out)
  You: Have you ever used a mobile phone?
  Marie: No, I have not used a mobile phone.
       (0.5 s, 254 tokens in, 11 out)

Answers: 12, average 1.3 s, fastest 0.5 s, slowest 2.5 s
```
