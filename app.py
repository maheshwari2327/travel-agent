import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agent import SYSTEM_PROMPT, build_agent

st.set_page_config(
    page_title="Travel Assistant Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner="Connecting to Ollama & LangGraph agent...")
def get_agent():
    return build_agent()


# Sidebar Configuration & Information
with st.sidebar:
    st.header("✈️ Travel Assistant")
    st.caption("Powered by LangGraph, Ollama (llama3.2) & Open-Meteo")

    st.markdown("---")
    st.subheader("💡 Quick Destinations")
    quick_destinations = [
        "Tokyo, Japan",
        "Paris, France",
        "New York, USA",
        "Cairo, Egypt",
        "Reykjavik, Iceland",
    ]

    selected_quick = None
    for city in quick_destinations:
        if st.button(f"📍 {city}", use_container_width=True):
            selected_quick = f"I'm planning a trip to {city}. What should I expect?"

    st.markdown("---")
    st.subheader("⚙️ System Status")
    st.markdown(
        """
        - **Model:** Ollama `llama3.2`
        - **Temperature:** `0.3`
        - **Tool:** `get_destination_info`
        - **Data:** Live Open-Meteo API
        """
    )

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main Header
st.title("🌍 AI Travel Assistant")
st.write(
    "Ask me about any travel destination! I will fetch real-time weather, forecast conditions, and provide tailored packing tips and activity recommendations."
)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your travel assistant. Where are you planning to go next?",
        }
    ]

# Display Existing Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle Quick Suggestion Click or Chat Input
user_query = st.chat_input("Where are you planning to travel?")
if selected_quick:
    user_query = selected_quick

if user_query:
    # Append and show user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Generate response
    with st.chat_message("assistant"):
        agent = get_agent()
        with st.spinner("Checking real-time weather and travel tips..."):
            try:
                # Build context messages including chat history
                history_messages = [SystemMessage(content=SYSTEM_PROMPT)]
                for m in st.session_state.messages[:-1]:
                    if m["role"] == "user":
                        history_messages.append(HumanMessage(content=m["content"]))
                    elif m["role"] == "assistant":
                        history_messages.append(AIMessage(content=m["content"]))
                history_messages.append(HumanMessage(content=user_query))

                result = agent.invoke({"messages": history_messages})
                response_text = result["messages"][-1].content
            except Exception as e:
                response_text = f"⚠️ An error occurred while contacting the agent: {e}"

            st.markdown(response_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
