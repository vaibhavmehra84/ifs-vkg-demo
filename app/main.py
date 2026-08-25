import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from app.agent import vkg_conversational_agent

st.set_page_config(page_title="IFS Virtual Knowledge Graph Assistant", layout="wide")
st.title("✈️ IFS Virtual Knowledge Graph Conversational Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

def render_step_logs(steps):
    with st.expander("🔍 View VKG Traversal, Reasoning & Tool Logs", expanded=False):
        for idx, step in enumerate(steps, 1):
            if step["type"] == "reasoning":
                st.markdown(f"**Step {idx}: 💭 LLM Reasoning & Intent**")
                st.info(step["content"])
            elif step["type"] == "tool_call":
                st.markdown(f"**Step {idx}: 🛠️ Invoking Tool** $\\rightarrow$ `{step['tool']}`")
                st.caption("Parameters passed to COTS / VKG Tool:")
                st.json(step["args"])
            elif step["type"] == "tool_result":
                st.markdown(f"**Step {idx}: 📦 Data Retrieved** $\\leftarrow$ `{step['tool']}`")
                st.caption("Payload retrieved from backend:")
                st.json(step["content"])
            st.divider()

# Render message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("steps"):
            render_step_logs(msg["steps"])

# Process input
if prompt := st.chat_input("Ask anything (e.g., 'Rank top 2 crew members in BOM for promotion')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    langgraph_input = []
    for m in st.session_state.messages:
        if m["role"] == "user":
            langgraph_input.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            langgraph_input.append(AIMessage(content=m["content"]))

    with st.chat_message("assistant"):
        with st.spinner("Traversing Virtual Knowledge Graph..."):
            response = vkg_conversational_agent.invoke({"messages": langgraph_input})
            new_msgs = response["messages"][len(langgraph_input):]
            
            steps = []
            final_reply = ""
            
            for m in new_msgs:
                # Extract LLM text blocks / reasoning
                reasoning_text = ""
                if isinstance(m, AIMessage):
                    if isinstance(m.content, str) and m.content.strip():
                        reasoning_text = m.content.strip()
                    elif isinstance(m.content, list):
                        text_blocks = [
                            block["text"] for block in m.content 
                            if isinstance(block, dict) and block.get("type") == "text" and block.get("text")
                        ]
                        if text_blocks:
                            reasoning_text = "\n".join(text_blocks).strip()

                # Tool Call Node (LLM decision point)
                if hasattr(m, "tool_calls") and m.tool_calls:
                    if reasoning_text:
                        steps.append({"type": "reasoning", "content": reasoning_text})
                    for tc in m.tool_calls:
                        steps.append({
                            "type": "tool_call",
                            "tool": tc["name"],
                            "args": tc["args"]
                        })
                # Tool Output Node
                elif isinstance(m, ToolMessage):
                    steps.append({
                        "type": "tool_result",
                        "tool": getattr(m, "name", "Tool"),
                        "content": m.content
                    })
                # Final Assistant Response
                elif isinstance(m, AIMessage) and reasoning_text:
                    final_reply = reasoning_text

            st.write(final_reply)
            
            if steps:
                render_step_logs(steps)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_reply,
                "steps": steps
            })