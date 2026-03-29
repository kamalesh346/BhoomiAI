import streamlit as st
from db.database import get_farmer, get_or_create_chat_session, update_chat_session
from agents.consultant import get_initial_greeting
from agents.agent_graph import run_agent_interaction
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def _to_langchain_messages(messages):
    """Convert list of dict messages to LangChain BaseMessage objects."""
    lc_messages = []
    for m in messages:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            lc_messages.append(AIMessage(content=m["content"]))
    return lc_messages

def render_chat():
    farmer_id = st.session_state.farmer_id
    farmer = get_farmer(farmer_id)

    st.markdown("""
    <div class="main-header">
        <div style="font-size:2.5rem;">💬</div>
        <div>
            <h2 style="margin:0;color:white;">Consultant Chat</h2>
            <p style="margin:0;opacity:0.8;font-size:0.9rem;">
                Your personal AI agricultural advisor — ask anything
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Session setup
    if "chat_session_id" not in st.session_state:
        try:
            session = get_or_create_chat_session(farmer_id)
            st.session_state.chat_session_id = session["id"]
            msgs = session.get("messages", [])
            if isinstance(msgs, str):
                import json
                msgs = json.loads(msgs)
            if not msgs:
                # Generate greeting
                greeting = get_initial_greeting(farmer)
                msgs = [{"role": "assistant", "content": greeting}]
            st.session_state.chat_messages = msgs
        except Exception as e:
            st.session_state.chat_session_id = None
            if not st.session_state.get("chat_messages"):
                st.session_state.chat_messages = [{
                    "role": "assistant",
                    "content": f"Namaste {farmer.get('name', '')}! 🙏 I'm Digital Sarathi, your farming advisor. What crop are you planning for this season?"
                }]

    # Suggested questions
    suggestions = [
        "Which crop is best for my soil this season?",
        "What government subsidies can I get?",
        "How should I manage water if monsoon is delayed?",
        "What pests should I watch out for?",
        "Is it good to try organic farming?",
    ]

    col_chat, col_tips = st.columns([3, 1])

    with col_tips:
        st.markdown("#### 💡 Quick Questions")
        for suggestion in suggestions:
            if st.button(suggestion[:35] + "...", key=f"sug_{suggestion[:15]}",
                         use_container_width=True):
                st.session_state.pending_message = suggestion

    with col_chat:
        # Chat display area
        chat_container = st.container(height=500)
        with chat_container:
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-bubble-user">
                        👨‍🌾 <strong>{farmer.get('name', 'You')}:</strong><br>{msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-bubble-bot">
                        🌾 <strong>Digital Sarathi:</strong><br>{msg['content']}
                    </div>
                    """, unsafe_allow_html=True)

        # Input area
        user_input = st.chat_input("Ask about crops, water, subsidies, pests...")

        # Handle suggestion click
        if "pending_message" in st.session_state:
            user_input = st.session_state.pop("pending_message")

        if user_input:
            # Add user message
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input
            })

            # Generate response
            with st.spinner("🌾 Digital Sarathi is thinking..."):
                try:
                    # Use the new agent graph interaction
                    lc_history = _to_langchain_messages(st.session_state.chat_messages[:-1])
                    result = run_agent_interaction(
                        user_input=user_input,
                        chat_history=lc_history,
                        farmer_profile=farmer
                    )
                    
                    response = result["message"]
                    rag_used = result.get("rag_used", False)

                    if rag_used:
                        response += "\n\n📚 *[Answer includes info from government scheme documents]*"

                except Exception as e:
                    response = f"I'm having trouble connecting right now. Please try again! (Error: {str(e)[:100]})"

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": response
            })

            # Save to DB
            try:
                if st.session_state.chat_session_id:
                    update_chat_session(
                        st.session_state.chat_session_id,
                        st.session_state.chat_messages,
                        {}
                    )
            except Exception:
                pass

            st.rerun()

    # Clear chat button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            greeting = get_initial_greeting(farmer)
            st.session_state.chat_messages = [{"role": "assistant", "content": greeting}]
            st.rerun()

    with col2:
        if st.button("🎯 Get Recommendations", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
