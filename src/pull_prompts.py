"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def _extract_message_template(message) -> str:
    """Extrai o texto de template de uma mensagem de um ChatPromptTemplate."""
    prompt = getattr(message, "prompt", message)
    return getattr(prompt, "template", str(message))


def pull_prompts_from_langsmith(prompt_name: str = PROMPT_NAME) -> dict:
    """
    Faz pull de um prompt do LangSmith Prompt Hub e o serializa usando a
    representação nativa do LangChain (ChatPromptTemplate.messages).

    Args:
        prompt_name: Nome do prompt no LangSmith Hub (ex: "usuario/nome_v1")

    Returns:
        Dicionário pronto para ser salvo em YAML
    """
    print(f"Puxando prompt do LangSmith Hub: {prompt_name}")
    prompt = hub.pull(prompt_name)
    print("   ✓ Prompt carregado com sucesso")

    system_prompt = ""
    user_prompt = ""

    for message in prompt.messages:
        role = message.__class__.__name__.lower()
        template = _extract_message_template(message)

        if "system" in role:
            system_prompt = template
        elif "human" in role or "user" in role:
            user_prompt = template

    key = prompt_name.split("/")[-1]

    return {
        key: {
            "description": f"Prompt puxado do LangSmith Hub ({prompt_name})",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "input_variables": list(prompt.input_variables),
        }
    }


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        prompt_data = pull_prompts_from_langsmith(PROMPT_NAME)
    except Exception as e:
        print(f"❌ Erro ao puxar prompt '{PROMPT_NAME}': {e}")
        return 1

    if not save_yaml(prompt_data, OUTPUT_PATH):
        print(f"❌ Falha ao salvar prompt em: {OUTPUT_PATH}")
        return 1

    print(f"✓ Prompt salvo em: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
