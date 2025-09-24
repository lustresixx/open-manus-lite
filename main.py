from src.config_loader import load_config

def main():
    cfg = load_config("config/config.toml")
    print("LLM model:", cfg.llm.model)
    print("Base URL:", cfg.llm.base_url)
    print("Temperature:", cfg.llm.temperature)
    print("Max tokens:", cfg.llm.max_tokens)
    print("API key (masked):", "***" if cfg.llm.api_key else "(empty)")

if __name__ == "__main__":
    main()
