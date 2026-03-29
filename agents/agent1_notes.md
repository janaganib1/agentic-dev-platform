client.messages.create(...)
```
This is where your API key is used. It sends your requirement to **Claude (claude-sonnet)** running on Anthropic's servers and gets the structured response back.

---

**What actually happened when you typed your requirement:**
```
Your input → Agent 1 → Anthropic API (Claude) → Structured Brief → Screen
```

Think of it like this — Agent 1 is just a **messenger with instructions**. It takes your plain English, wraps it in a professional prompt, sends it to Claude, and returns the answer formatted nicely.

---

**The "prompt" is the intelligence**
The real brain is in this part:
```
"You are a software project orchestrator..."