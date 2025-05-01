import streamlit as st
import requests
import json

# Configuração da página
st.set_page_config(
    page_title="Palavra Certa - Gerador de Mensagens",
    page_icon="✉️",
    layout="centered"
)

# Título e descrição
st.title("✉️ Palavra Certa")
st.markdown("""
    **Gere mensagens personalizadas em segundos com IA!**
    
    Escolha o tipo de mensagem, preencha os detalhes contextuais e receba uma mensagem pronta para enviar.
""")

# Função para fazer requisição à API do Deepseek via Hugging Face
def generate_message(prompt, token):
    API_URL = "https://router.huggingface.co/novita/v3/openai/chat/completions"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "Você é um assistente especializado em criar mensagens personalizadas. Sua tarefa é gerar mensagens claras, empáticas e bem escritas com base nas instruções do usuário."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 512,
        "model": "deepseek/deepseek-prover-v2-671b"
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# Dicionário de tipos de mensagens com campos personalizados
message_types = {
    "Aniversário": ["nome_pessoa", "relacionamento", "tom"],
    "Desculpas": ["nome_pessoa", "motivo", "tom"],
    "Parabéns": ["nome_pessoa", "conquista", "relacionamento"],
    "Networking": ["nome_pessoa", "contexto", "objetivo"],
    "Vendas": ["nome_cliente", "produto", "benefícios"],
    "Agradecimento": ["nome_pessoa", "motivo", "tom"],
    "Convite": ["nome_pessoa", "evento", "data_hora", "local"],
    "Motivacional": ["nome_pessoa", "situação", "tom"],
}

# Opções para o tom da mensagem
tom_options = ["Casual", "Formal", "Amigável", "Profissional", "Engraçado", "Sério", "Emocionante"]

# Opções para o meio de envio
meio_options = ["WhatsApp", "E-mail", "SMS", "LinkedIn", "Instagram", "Facebook", "Twitter"]

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações")
    
    # Opção para inserir token próprio
    use_custom_token = st.checkbox("Usar meu próprio token da Hugging Face")
    
    if use_custom_token:
        hf_token = st.text_input("Token da Hugging Face", type="password")
    else:
        try:
            hf_token = st.secrets["huggingface"]["token"]
        except:
            hf_token = ""
            st.error("Token não encontrado. Por favor, insira seu token manualmente.")
    
    # Informações do modelo
    st.markdown("---")
    st.markdown("### Sobre")
    st.markdown("Desenvolvido com ❤️ usando o modelo Deepseek")
    st.markdown("Modelo: deepseek/deepseek-prover-v2-671b")
    st.markdown("[GitHub do Projeto](https://github.com/seu-usuario/palavra-certa)")

# Área principal
# Seleção do tipo de mensagem
message_type = st.selectbox(
    "Tipo de mensagem",
    list(message_types.keys())
)

# Campos dinâmicos com base no tipo de mensagem selecionado
st.subheader("Detalhes da mensagem")

# Criar um dicionário para armazenar os valores dos campos
field_values = {}

# Gerar campos específicos para o tipo de mensagem
col1, col2 = st.columns(2)
with col1:
    for i, field in enumerate(message_types[message_type][:len(message_types[message_type])//2 + len(message_types[message_type])%2]):
        display_name = field.replace("_", " ").title()
        
        # Campo especial para tom, se existir
        if field == "tom":
            field_values[field] = st.selectbox(display_name, tom_options)
        else:
            field_values[field] = st.text_input(display_name)

with col2:
    for i, field in enumerate(message_types[message_type][len(message_types[message_type])//2 + len(message_types[message_type])%2:]):
        display_name = field.replace("_", " ").title()
        
        # Campo especial para tom, se existir
        if field == "tom":
            field_values[field] = st.selectbox(display_name, tom_options)
        else:
            field_values[field] = st.text_input(display_name)

# Meio de envio
meio = st.selectbox("Meio de envio", meio_options)

# Comprimento da mensagem
message_length = st.select_slider(
    "Comprimento da mensagem",
    options=["Curta", "Média", "Longa"],
    value="Média"
)

# Botão para gerar mensagem
if st.button("✨ Gerar Mensagem", type="primary", use_container_width=True):
    # Verificar se todos os campos estão preenchidos
    if all(field_values.values()) and hf_token:
        with st.spinner("Gerando mensagem personalizada..."):
            # Construir o prompt para a IA
            prompt = f"""Por favor, crie uma mensagem de {message_type.lower()} com as seguintes características:

Detalhes:
"""
            
            for field, value in field_values.items():
                prompt += f"- {field.replace('_', ' ').title()}: {value}\n"
            
            prompt += f"\nMeio de envio: {meio}\n"
            
            # Ajustar comprimento de acordo com a opção
            if message_length == "Curta":
                prompt += "Comprimento: Curta (máximo 3 frases)\n"
            elif message_length == "Média":
                prompt += "Comprimento: Média (entre 4 e 6 frases)\n"
            else:
                prompt += "Comprimento: Longa (entre 7 e 10 frases, com detalhes)\n"
                
            prompt += "\nCrie uma mensagem pronta para ser enviada, sem comentários adicionais. A mensagem deve ser empática, clara e adequada ao contexto."
            
            try:
                # Fazer requisição à API
                result = generate_message(prompt, hf_token)
                
                # Extrair a mensagem da resposta do Deepseek
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0]["message"]["content"]
                else:
                    message = ""
                    
                    # Verificar se há um erro específico na resposta
                    if "error" in result:
                        st.error(f"Erro da API: {result['error']['message']}")
                    else:
                        st.error("Não foi possível gerar a mensagem. Verifique o token e tente novamente.")
                
                if message:
                    # Exibir resultado em um contêiner estilizado
                    st.subheader("Mensagem Gerada:")
                    st.markdown("---")
                    message_container = st.container()
                    with message_container:
                        st.markdown(f"<div style='background-color:#f0f2f6;padding:20px;border-radius:10px;'>{message}</div>", unsafe_allow_html=True)
                    
                    # Botão para copiar a mensagem
                    st.markdown("---")
                    st.markdown("""
                    <div style="display: flex; justify-content: center; margin-top: 10px;">
                        <button 
                            onclick="
                                navigator.clipboard.writeText(document.querySelector('.stMarkdown div').innerText);
                                this.innerText='✓ Copiado!';
                                setTimeout(() => this.innerText='📋 Copiar Mensagem', 2000)
                            " 
                            style="background-color:#4CAF50;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;"
                        >
                            📋 Copiar Mensagem
                        </button>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao gerar mensagem: {str(e)}")
    else:
        if not hf_token:
            st.error("Por favor, insira um token válido da Hugging Face.")
        else:
            st.warning("Por favor, preencha todos os campos para gerar a mensagem.")

# Dicas de uso
with st.expander("📚 Dicas de uso"):
    st.markdown("""
    ### Como usar o Palavra Certa:
    
    1. **Escolha o tipo de mensagem** que você deseja gerar
    2. **Preencha os detalhes** específicos para personalizar sua mensagem
    3. **Selecione o meio** onde a mensagem será enviada
    4. **Ajuste o comprimento** de acordo com sua necessidade
    5. Clique em **Gerar Mensagem**
    6. **Copie** o resultado e envie!
    
    Para melhores resultados, forneça informações específicas e claras nos campos de detalhes.
    """)

# Feedback
with st.expander("💬 Feedback"):
    st.markdown("""
    Sua opinião é importante para melhorarmos o Palavra Certa!
    
    [Enviar feedback](mailto:seu-email@exemplo.com) | [Reportar um problema](https://github.com/seu-usuario/palavra-certa/issues)
    """)
