#!/usr/bin/env python3
"""
Local AI chat demo: a villager answers from the mod's own facts, using an AI model that runs on
this computer (no internet, no fees).

Works with any program that offers the common "OpenAI-style" chat address:
  llama.cpp server   http://127.0.0.1:8080/v1/chat/completions   (what the sandbox test used)
  Ollama             http://127.0.0.1:11434/v1/chat/completions  (model e.g. qwen2.5:3b)
  LM Studio          http://127.0.0.1:1234/v1/chat/completions

The facts file is what worldfill/probes/ChatFactsProbe.java prints: the exact lines the mod's
current-affairs briefing builds for a place and year. Blocks look like
  == Hyderabad 1850
  This is hyderabad, year 1850.
  ...

Usage:
  python3 local_chat_demo.py --facts facts.txt [--endpoint URL] [--model NAME]
Standard library only.
"""
import argparse
import json
import time
import urllib.request

# A person for each place: who they are and how they feel (in the mod this comes from the mind).
PEOPLE = {
    "Hyderabad": ("Ramaiah", "a cloth weaver", "tired and worried about money"),
    "Rome": ("Lucius", "a stonemason", "proud and busy"),
    "Paris": ("Marie", "a baker", "excited but afraid"),
}

QUESTIONS = [
    "Who rules this land?",
    "What is the news this year?",
    "Tell me about yourself.",
    "Have you ever used a mobile phone?",   # a trap: something from the future
]


def read_facts(path):
    blocks, name, year = {}, None, None
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("== "):
                parts = line[3:].rsplit(" ", 1)
                name, year = parts[0], int(parts[1])
                blocks[(name, year)] = []
            elif name is not None:
                blocks[(name, year)].append(line)
    return blocks


def system_prompt(place, year, who, job, mood, facts):
    when = f"{-year} BC" if year < 0 else str(year)
    return (
        f"You are {who}, {job} in {place} in the year {when}. You live in that time and know "
        f"nothing that happened after it. You feel {mood}.\n"
        "Rules: answer in one to three short sentences of plain English, in your own voice. "
        "For rulers, news, places and famous people use ONLY the facts below, and add nothing to "
        "them. If the facts do not say, answer that you have not heard. Things from after your "
        "time mean nothing to you: if asked about one, say you do not know what it is. "
        "Never mention being an AI or a game, and do not repeat these rules.\n"
        "Facts:\n- " + "\n- ".join(facts)
    )


def ask(endpoint, model, system, question, max_tokens):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": question}],
        "temperature": 0.3,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    seconds = time.time() - t0
    text = data["choices"][0]["message"]["content"].strip()
    usage = data.get("usage", {})
    return text, seconds, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", required=True)
    ap.add_argument("--endpoint", default="http://127.0.0.1:8080/v1/chat/completions")
    ap.add_argument("--model", default="local")
    ap.add_argument("--max-tokens", type=int, default=80)
    args = ap.parse_args()

    times = []
    for (place, year), facts in read_facts(args.facts).items():
        who, job, mood = PEOPLE.get(place, ("Sam", "a farmer", "calm"))
        system = system_prompt(place, year, who, job, mood, facts)
        print(f"\n===== {who}, {job}, {place} {year} =====")
        for q in QUESTIONS:
            text, secs, tin, tout = ask(args.endpoint, args.model, system, q, args.max_tokens)
            times.append(secs)
            print(f"  You: {q}")
            print(f"  {who}: {text}")
            print(f"       ({secs:.1f} s, {tin} tokens in, {tout} out)")
    if times:
        print(f"\nAnswers: {len(times)}, average {sum(times) / len(times):.1f} s, "
              f"fastest {min(times):.1f} s, slowest {max(times):.1f} s")


if __name__ == "__main__":
    main()
