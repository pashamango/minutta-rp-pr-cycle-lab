# Sovereign worker runway slice

This small fail-closed experiment routes sensitive goals to loopback Ollama and
leaves low-sensitivity goals at an explicit Gemini authentication boundary. It
never reads a provider secret or writes a credential file.

Reproduce with:

```sh
python3 -m unittest discover -s sovereign_worker -p 'test_*.py' -v
```

The actual local call requires Ollama at `127.0.0.1:11434` and a local model.
